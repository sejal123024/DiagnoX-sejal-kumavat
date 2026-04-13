"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FiHome, FiActivity, FiUser, FiSettings, FiBell, FiCamera, FiMic, 
  FiUpload, FiDownload, FiShare2, FiHeart, FiLogOut
} from "react-icons/fi";
import Image from "next/image";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { auth } from "../../lib/firebase";
import { onAuthStateChanged, signOut, User } from "firebase/auth";

const Spline = dynamic(() => import('@splinetool/react-spline'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-[#050505] animate-pulse rounded-[2rem]" />
});
// Colors defined in the prompt:
// Background: #0B0B0B
// Primary Accent: #00FFA3 (Neon Green)
// Alerts: Soft Red

const GLOW_GREEN = "#00FFA3";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<null | any>(null);
  const [scanError, setScanError] = useState<string | null>(null);

  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Greeting logic
  const [greeting, setGreeting] = useState("Good Evening");
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 18) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  // Authentication monitoring
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        router.push('/');
      }
    });
    return () => unsubscribe();
  }, [router]);

  // ── Send audio blob to the backend for real AI analysis ──
  const analyzeAudio = useCallback(async (audioBlob: Blob, fileName: string) => {
    setIsScanning(true);
    setScanResult(null);
    setScanError(null);

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, fileName);

      // Attach auth token & userId if logged in
      if (user) {
        const token = await user.getIdToken();
        formData.append("token", token);
        formData.append("userId", user.email || user.uid);
      }

      const response = await fetch("/api/scan", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || errData.details || `Backend returned ${response.status}`);
      }

      const data = await response.json();

      // Map backend response to the UI result format
      setScanResult({
        title: data.predicted_disease || "Analysis",
        value: data.explanation || `Detected: ${data.predicted_disease}`,
        risk: data.risk_level || "Unknown",
        conf: `${data.probability?.toFixed(1) || 0}%`,
        // Extended data from backend
        allProbabilities: data.all_probabilities || {},
        diagnostics: data.diagnostics || {},
        alerts: data.alerts || [],
      });
    } catch (err: any) {
      console.error("Analysis failed:", err);
      setScanError(err.message || "Failed to analyze audio. Is the Python backend running on port 8000?");
    } finally {
      setIsScanning(false);
    }
  }, [user]);

  // ── Start live microphone recording ──
  const handleStartRecording = useCallback(async () => {
    setScanError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks to release the microphone
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await analyzeAudio(audioBlob, "live_recording.webm");
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err: any) {
      console.error("Mic error:", err);
      setScanError("Microphone access denied. Please allow microphone permissions in your browser.");
    }
  }, [analyzeAudio]);

  // ── Stop recording ──
  const handleStopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  // ── Handle file upload ──
  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      analyzeAudio(file, file.name);
    }
    // Reset input so same file can be re-selected
    e.target.value = "";
  }, [analyzeAudio]);

  return (
    <div className="min-h-screen bg-[#0B0B0B] text-white flex font-sans select-none relative">
      
      {/* ---------------- SIDEBAR ---------------- */}
      <motion.aside 
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-24 lg:w-64 h-screen sticky top-0 border-r border-[#00FFA3]/10 bg-black/40 backdrop-blur-3xl flex flex-col items-center lg:items-start py-10 z-20"
      >
        <div className="px-0 lg:px-8 mb-16 flex items-center justify-center lg:justify-start w-full">
          <div className="w-10 h-10 rounded-xl bg-[#00FFA3]/10 border border-[#00FFA3]/40 shadow-[0_0_15px_#00FFA3] flex items-center justify-center">
            <FiActivity className="text-[#00FFA3] text-xl" />
          </div>
          <span className="hidden lg:block ml-4 text-xl font-bold tracking-widest uppercase">Vita<span className="text-[#00FFA3]">Scan</span></span>
        </div>

        <nav className="flex-1 w-full space-y-4 px-4 lg:px-6">
          {[
            { id: "overview", icon: FiHome, label: "Overview" },
            { id: "asthma", icon: FiMic, label: "Asthma" },
            { id: "parkinsons", icon: FiActivity, label: "Parkinson's" },
            { id: "healthy", icon: FiHeart, label: "Healthy Status" },
            { id: "depression", icon: FiUser, label: "Depression" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-center lg:justify-start gap-4 p-4 rounded-2xl transition-all duration-300 relative group overflow-hidden ${
                activeTab === item.id 
                  ? "bg-[#00FFA3]/10 border border-[#00FFA3]/30 shadow-[0_0_20px_rgba(0,255,163,0.15)] text-[#00FFA3]" 
                  : "hover:bg-white/5 text-gray-500 hover:text-white"
              }`}
            >
              {activeTab === item.id && (
                <motion.div layoutId="activeTabIndicator" className="absolute left-0 top-0 bottom-0 w-1 bg-[#00FFA3] shadow-[0_0_10px_#00FFA3]" />
              )}
              <item.icon className={`text-2xl ${activeTab === item.id ? 'drop-shadow-[0_0_8px_#00FFA3]' : ''}`} />
              <span className="hidden lg:block font-medium tracking-wide">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto w-full px-4 lg:px-6">
          <div className="text-gray-500 hover:text-white transition-colors cursor-pointer flex justify-center lg:justify-start items-center gap-4 p-4">
            <FiSettings className="text-2xl" />
            <span className="hidden lg:block font-medium">Settings</span>
          </div>
          <div 
            onClick={() => signOut(auth)}
            className="text-red-500/60 hover:text-red-500 hover:bg-red-500/10 rounded-2xl transition-all cursor-pointer flex justify-center lg:justify-start items-center gap-4 p-4 mt-2"
          >
            <FiLogOut className="text-2xl" />
            <span className="hidden lg:block font-medium">Log out</span>
          </div>
        </div>
      </motion.aside>

      {/* ---------------- MAIN CONTENT ---------------- */}
      <main className="flex-1 min-h-screen relative perspective-1000 w-full">
        
        {/* Background Ambient Glow */}
        <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
          <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#00FFA3]/5 blur-[150px] rounded-full mix-blend-screen" />
          <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#00FFA3]/5 blur-[150px] rounded-full mix-blend-screen" />
        </div>

        {/* TOP NAVBAR */}
        <header className="w-full h-24 flex items-center justify-between px-10 relative z-10">
          <div>
            <motion.h1 
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="text-3xl font-light tracking-wide text-white"
            >
              {greeting}, <span className="font-bold">{user?.displayName || user?.email?.split('@')[0] || "Guest"}</span> 👋
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
              className="text-[#00FFA3] mt-1 text-sm tracking-widest uppercase"
            >
              Your body insights are ready
            </motion.p>
          </div>
          
          <div className="flex items-center gap-6">
            <button className="relative w-12 h-12 rounded-full border border-white/10 bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors">
              <FiBell className="text-xl text-gray-300" />
              <span className="absolute top-3 right-3 w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_#ef4444]"></span>
            </button>
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#00FFA3] to-teal-800 p-[2px] shadow-[0_0_15px_rgba(0,255,163,0.3)]">
              <div className="w-full h-full bg-black rounded-full flex items-center justify-center overflow-hidden">
                <Image src="/features/anemia.png" alt="Profile" width={48} height={48} className="object-cover opacity-80" sizes="48px" />
              </div>
            </div>
          </div>
        </header>

        <div className="px-10 pb-20 relative z-10 w-full max-w-[1600px] mx-auto min-h-[calc(100vh-100px)] flex flex-col justify-center">
          
          <AnimatePresence mode="wait">
            
            {/* OVERVIEW TAB */}
            {activeTab === "overview" && (
              <motion.div 
                key="overview"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="flex flex-col gap-8 w-full"
              >
                
                {/* ---------- ROW 1: SPLINE HERO ---------- */}
                <div className="w-full relative h-[500px] rounded-[2rem] border border-white/5 bg-black overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex mb-4">
                  
                  {/* Left: Text Content & CTA */}
                  <div className="relative z-20 flex flex-col justify-center p-12 w-1/2 bg-black">
                    <motion.div 
                      initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
                    >
                      <h2 className="text-5xl md:text-6xl font-light mb-6">No scans <span className="font-bold text-[#00FFA3]">yet</span></h2>
                      <p className="text-gray-400 mb-10 max-w-md text-xl font-light leading-relaxed">
                        Start your first body scan to unlock AI-driven insights into your physiological state.
                      </p>
                      <button 
                        onClick={() => setActiveTab("asthma")}
                        className="px-10 py-5 w-max rounded-full bg-[#00FFA3] text-black font-bold uppercase tracking-widest text-sm shadow-[0_0_30px_rgba(0,255,163,0.4)] hover:shadow-[0_0_50px_rgba(0,255,163,0.6)] hover:scale-105 transition-all flex items-center gap-3"
                      >
                        <FiActivity className="text-xl" />
                        Start Scan
                      </button>
                    </motion.div>
                  </div>

                  {/* Right: Spline 3D Viewer Container */}
                  <div className="relative w-1/2 h-full z-10 pointer-events-auto bg-black">
                    {/* Perfect seamless gradient fade on the left edge */}
                    <div className="absolute top-0 bottom-0 left-0 w-32 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none" />
                    
                    <div className="w-full h-full pointer-events-none">
                      <Spline scene="https://prod.spline.design/YxmQhENbdrbvHB0K/scene.splinecode" style={{ width: '100%', height: '100%' }} />
                    </div>

                    {/* Watermark Cover Box over the spline logo */}
                    <div className="absolute bottom-0 right-0 w-[180px] h-[60px] bg-black z-50 pointer-events-none rounded-br-[2rem]" />
                  </div>
                </div>

                {/* ---------- ROW 2: SYSTEM STATUS ---------- */}
                <div className="w-full rounded-[2rem] border border-white/5 bg-black/40 backdrop-blur-3xl p-8 flex flex-col justify-between shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
                  <div>
                    <h3 className="text-xs font-semibold text-[#00FFA3] tracking-[0.2em] uppercase mb-8 flex items-center gap-2">
                      <div className="w-2 h-2 bg-[#00FFA3] rounded-full animate-pulse blur-[1px]"></div>
                      System Status
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {[
                        { label: "AI Engine Status", val: "Active", icon: <FiActivity />, col: "text-[#00FFA3]" },
                        { label: "Model Accuracy", val: "Loaded", icon: <FiUpload />, col: "text-white" },
                        { label: "Camera Access", val: "Ready", icon: <FiCamera />, col: "text-white" },
                        { label: "Audio Input", val: "Available", icon: <FiMic />, col: "text-white" },
                      ].map((stat, i) => (
                        <div key={i} className="flex justify-between items-center bg-white/[0.02] hover:bg-white/[0.04] transition-colors p-6 rounded-2xl border border-white/5">
                          <span className="text-gray-400 text-sm flex items-center gap-3">
                            <span className="text-gray-500">{stat.icon}</span> {stat.label}
                          </span>
                          <span className={`text-lg font-medium tracking-wide ${stat.col}`}>{stat.val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* ---------- ROW 2: SCAN STATUS CARDS (Not Results) ---------- */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {[
                    { title: "Asthma", status: "Not Scanned", icon: <FiMic />, type: "asthma" },
                    { title: "Parkinson's", status: "Pending", icon: <FiActivity />, type: "parkinsons" },
                    { title: "Healthy Status", status: "Not Started", icon: <FiHeart />, type: "healthy" },
                    { title: "Depression", status: "Awaiting Input", icon: <FiUser />, type: "depression" },
                  ].map((card, idx) => (
                    <motion.div 
                      key={idx}
                      whileHover={{ y: -5 }}
                      onClick={() => setActiveTab(card.type)}
                      className="bg-black/40 border border-white/5 hover:border-white/20 hover:shadow-[0_0_30px_rgba(255,255,255,0.05)] rounded-[2rem] p-8 backdrop-blur-xl flex flex-col justify-between h-[220px] transition-all cursor-pointer group"
                    >
                      <div className="flex justify-between items-start">
                        <div className="w-12 h-12 rounded-full bg-white/[0.03] border border-white/10 flex items-center justify-center text-xl text-gray-400 group-hover:text-white transition-colors">
                          {card.icon}
                        </div>
                        <div className="px-3 py-1 bg-white/[0.05] rounded-full text-xs text-gray-500 font-mono">
                          {card.status}
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-gray-400 font-medium tracking-wide text-sm mb-1 uppercase">Scan Module</h3>
                        <div className="text-xl font-light text-white">{card.title}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* ---------- ROW 3: RECENT ACTIVITY & TRUST ---------- */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  
                  {/* Recent Activity Feed */}
                  <div className="rounded-[2rem] border border-white/5 bg-black/40 backdrop-blur-3xl p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col">
                    <h3 className="text-xs font-semibold text-gray-400 tracking-[0.2em] uppercase mb-8">Recent Activity</h3>
                    <div className="space-y-6 flex-1">
                      <div className="flex gap-4">
                        <div className="mt-1"><div className="w-2 h-2 rounded-full bg-gray-500"></div></div>
                        <div>
                          <p className="text-sm font-light text-gray-300">Neural models loaded successfully into memory.</p>
                          <p className="text-xs text-gray-600 mt-1 font-mono">SYS_INIT • 2 mins ago</p>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="mt-1"><div className="w-2 h-2 rounded-full bg-gray-500"></div></div>
                        <div>
                          <p className="text-sm font-light text-gray-300">User authenticated via external token.</p>
                          <p className="text-xs text-gray-600 mt-1 font-mono">AUTH_SUCCESS • 2 mins ago</p>
                        </div>
                      </div>
                      <div className="flex gap-4 relative">
                        <div className="absolute -left-2.5 top-0 bottom-0 w-[1px] bg-[#00FFA3]/30"></div>
                        <div className="mt-1 -ml-[1px] z-10"><div className="w-2 h-2 rounded-full bg-[#00FFA3] shadow-[0_0_8px_#00FFA3]"></div></div>
                        <div>
                          <p className="text-sm font-light text-white">Awaiting initial biometric input... Ready to process.</p>
                          <p className="text-xs text-[#00FFA3]/70 mt-1 font-mono">STATUS_WAITING • Just now</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Educational & Trust Section */}
                  <div className="rounded-[2rem] border border-white/5 bg-black/40 backdrop-blur-3xl p-10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden relative group">
                    {/* Background glow accent */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/[0.02] rounded-full blur-[80px] group-hover:bg-[#00FFA3]/10 transition-colors duration-700 pointer-events-none"></div>
                    
                    <h3 className="text-xs font-semibold text-gray-400 tracking-[0.2em] uppercase mb-8">How VitaScan Works</h3>
                    <ul className="space-y-6 relative z-10">
                      <li className="flex items-start gap-5">
                        <div className="text-xl font-black text-transparent" style={{ WebkitTextStroke: '1px rgba(255,255,255,0.3)' }}>01</div>
                        <div>
                          <p className="text-white text-sm font-medium mb-1">Select an AI Scan Module</p>
                          <p className="text-gray-500 text-sm font-light">Choose from Asthma, Parkinson's, Healthy Status, or Depression from the sidebar.</p>
                        </div>
                      </li>
                      <li className="flex items-start gap-5">
                        <div className="text-xl font-black text-transparent" style={{ WebkitTextStroke: '1px rgba(255,255,255,0.3)' }}>02</div>
                        <div>
                          <p className="text-white text-sm font-medium mb-1">Provide Biometric Input</p>
                          <p className="text-gray-500 text-sm font-light">Grant camera or microphone permissions to allow our secure neural engine to capture your state.</p>
                        </div>
                      </li>
                      <li className="flex items-start gap-5">
                        <div className="text-xl font-black text-transparent" style={{ WebkitTextStroke: '1px rgba(0,255,163,0.5)' }}>03</div>
                        <div>
                          <p className="text-[#00FFA3] text-sm font-medium mb-1">Immediate Insights</p>
                          <p className="text-gray-500 text-sm font-light">Our locally-hosted algorithms analyze the input in real-time, delivering privacy-first, accurate health inferences directly on your device.</p>
                        </div>
                      </li>
                    </ul>
                  </div>

                </div>

              </motion.div>
            )}

            {/* SCANNER MODULE REUSABLE LAYOUT */}
            {activeTab !== "overview" && (
              <motion.div 
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
                className="w-full h-[700px] border border-white/10 rounded-[3rem] bg-black/40 backdrop-blur-3xl overflow-hidden relative shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col items-center justify-center"
              >
                {/* Corner Accents */}
                <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-[#00FFA3]/50 rounded-tl-[3rem]"></div>
                <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-[#00FFA3]/50 rounded-br-[3rem]"></div>

                {/* Hidden file input for upload */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*,.wav,.mp3,.ogg,.webm"
                  className="hidden"
                  onChange={handleFileUpload}
                />

                {isScanning ? (
                  <div className="flex flex-col items-center justify-center">
                    <div className="w-32 h-32 rounded-full border-2 border-white/10 border-t-[#00FFA3] animate-spin mb-8 shadow-[0_0_30px_rgba(0,255,163,0.3)]"></div>
                    <h2 className="text-2xl font-light tracking-widest uppercase text-[#00FFA3] animate-pulse">Analyzing Voice Biomarkers...</h2>
                    <p className="text-gray-500 mt-4 max-w-md text-center">Processing audio through the AI diagnostic pipeline. Extracting 150-dimensional vocal feature vectors...</p>
                  </div>
                ) : scanError ? (
                  <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center text-center max-w-xl">
                    <div className="w-24 h-24 bg-red-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(239,68,68,0.2)]">
                      <FiActivity className="text-4xl text-red-400" />
                    </div>
                    <h2 className="text-2xl font-light text-white mb-4">Analysis Failed</h2>
                    <p className="text-red-400/80 mb-8 leading-relaxed">{scanError}</p>
                    <button onClick={() => setScanError(null)} className="px-8 py-3 rounded-full bg-[#00FFA3] text-black font-bold uppercase tracking-wider text-xs shadow-[0_0_20px_rgba(0,255,163,0.4)]">
                      Try Again
                    </button>
                  </motion.div>
                ) : scanResult ? (
                  <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center text-center w-full max-w-3xl">
                    <div className="w-24 h-24 bg-[#00FFA3]/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(0,255,163,0.4)]">
                      <FiActivity className="text-4xl text-[#00FFA3]" />
                    </div>
                    <h2 className="text-4xl font-light text-white mb-2">{scanResult.title} Complete</h2>
                    <div className="text-[#00FFA3] text-lg font-medium mb-6 max-w-lg leading-relaxed">{scanResult.value}</div>
                    
                    <div className="flex gap-4 mb-6">
                      <div className="px-6 py-3 bg-black/50 border border-white/10 rounded-2xl">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Risk Assessment</p>
                        <p className={`text-lg font-semibold ${
                          scanResult.risk === "High" ? "text-red-400" :
                          scanResult.risk === "Medium" ? "text-yellow-400" : "text-[#00FFA3]"
                        }`}>{scanResult.risk}</p>
                      </div>
                      <div className="px-6 py-3 bg-black/50 border border-white/10 rounded-2xl">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">AI Confidence</p>
                        <p className="text-lg text-white">{scanResult.conf}</p>
                      </div>
                    </div>

                    {/* Probability Breakdown */}
                    {scanResult.allProbabilities && Object.keys(scanResult.allProbabilities).length > 0 && (
                      <div className="w-full mb-6 px-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Disease Probability Breakdown</p>
                        <div className="space-y-2">
                          {Object.entries(scanResult.allProbabilities)
                            .sort(([,a]: any, [,b]: any) => b - a)
                            .map(([disease, prob]: [string, any]) => (
                              <div key={disease} className="flex items-center gap-3">
                                <span className="text-gray-400 text-sm w-40 text-right truncate">{disease}</span>
                                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${prob}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    className={`h-full rounded-full ${
                                      prob > 60 ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" :
                                      prob > 30 ? "bg-yellow-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" :
                                      "bg-[#00FFA3] shadow-[0_0_8px_rgba(0,255,163,0.5)]"
                                    }`}
                                  />
                                </div>
                                <span className="text-white text-sm w-16 font-mono">{prob.toFixed(1)}%</span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Alerts */}
                    {scanResult.alerts && scanResult.alerts.length > 0 && (
                      <div className="w-full mb-6 px-4">
                        {scanResult.alerts.map((alert: string, i: number) => (
                          <div key={i} className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-2 text-red-400 text-sm text-left">
                            🚨 {alert}
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-4">
                      <button className="px-8 py-3 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors flex items-center gap-2">
                        <FiDownload /> Download Report
                      </button>
                      <button onClick={() => { setScanResult(null); setScanError(null); }} className="px-8 py-3 rounded-full bg-[#00FFA3] text-black font-bold uppercase tracking-wider text-xs shadow-[0_0_20px_rgba(0,255,163,0.4)]">
                        New Scan
                      </button>
                    </div>
                  </motion.div>
                ) : (
                  <div className="flex flex-col items-center text-center max-w-2xl px-10">
                    <div className="text-[#00FFA3] mb-6">
                      {activeTab === "asthma" && <FiMic className="text-6xl mx-auto drop-shadow-[0_0_15px_#00FFA3]" />}
                      {activeTab === "parkinsons" && <FiActivity className="text-6xl mx-auto drop-shadow-[0_0_15px_#00FFA3]" />}
                      {activeTab === "healthy" && <FiHeart className="text-6xl mx-auto drop-shadow-[0_0_15px_#00FFA3]" />}
                      {activeTab === "depression" && <FiUser className="text-6xl mx-auto drop-shadow-[0_0_15px_#00FFA3]" />}
                    </div>
                    
                    <h2 className="text-4xl font-light text-white mb-4 uppercase tracking-widest">
                      {activeTab === "asthma" ? "Respiratory / Asthma Scan" :
                       activeTab === "parkinsons" ? "Neurological Tremor Scan" :
                       activeTab === "healthy" ? "Baseline Health Scan" : "Cognitive Depression Scan"}
                    </h2>
                    
                    <p className="text-gray-400 text-lg mb-10 leading-relaxed">
                      {activeTab === "asthma" ? "Record 5 seconds of your breathing or cough in a quiet environment to detect wheezing." :
                       activeTab === "parkinsons" ? "Read the provided text aloud clearly to assess vocal tremors and micro-stutters." :
                       activeTab === "healthy" ? "Establish your voice baseline. Speak naturally for 10 seconds." : "Describe your day naturally to analyze speech tone, pauses, and emotional energy."}
                    </p>

                    <div className="flex gap-6">
                      <button 
                        onClick={isRecording ? handleStopRecording : handleStartRecording}
                        className={`px-8 py-4 rounded-full font-bold uppercase tracking-wider text-sm shadow-[0_0_20px_rgba(0,255,163,0.4)] hover:shadow-[0_0_40px_rgba(0,255,163,0.6)] transition-all flex items-center gap-2 ${
                          isRecording
                            ? "bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)] hover:shadow-[0_0_40px_rgba(239,68,68,0.6)] animate-pulse"
                            : "bg-[#00FFA3] text-black"
                        }`}
                      >
                        <FiMic /> {isRecording ? "Stop Recording" : "Start Recording"}
                      </button>
                      <button 
                        onClick={() => fileInputRef.current?.click()}
                        className="px-8 py-4 rounded-full border border-white/20 hover:bg-white/5 transition-all uppercase tracking-wider text-sm flex items-center gap-2"
                      >
                        <FiUpload /> Upload File
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </main>

      {/* Global CSS for custom animations omitted for brevity but utilizing tailwind config later if needed */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes pulse-slow {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(0.98); }
        }
        .animate-pulse-slow {
          animation: pulse-slow 4s ease-in-out infinite;
        }
      `}} />
    </div>
  );
}
