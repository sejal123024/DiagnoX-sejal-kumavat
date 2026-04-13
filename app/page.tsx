"use client";

import { motion } from "framer-motion";
import Script from "next/script";
import Image from "next/image";
import Link from "next/link";
import dynamic from "next/dynamic";

const Spline = dynamic(() => import('@splinetool/react-spline'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-[#050505] animate-pulse rounded-2xl" />
});

import React from 'react';
import ParticleSponsors from "./components/ParticleSponsors";
import Reveal from "./components/Reveal";

export default function Home() {
  return (
    <main className="bg-[#050505] text-white overflow-x-clip">

      {/* ================= NAVBAR ================= */}
      <nav className="fixed top-0 w-full z-50 flex justify-between items-center px-10 py-4 backdrop-blur-lg bg-black/30 border-b border-white/10">
        
        <h1 className="text-xl font-bold text-[#14B8A6]">VitaScan</h1>

        <div className="hidden md:flex gap-8 text-sm">
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#features">Features</a>
          <a href="#sponsorship">Sponsorship</a>
          <a href="#contact">Contact</a>
        </div>

        <div className="flex gap-3">
          <a href="/login?mode=signin">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              className="px-6 py-2 rounded-full border border-[#14B8A6] text-[#14B8A6] hover:bg-[#14B8A6]/10 transition-colors text-sm font-bold"
            >
              Login
            </motion.button>
          </a>
          
          <a href="/login?mode=signup">
            <motion.button 
              whileHover={{ scale: 1.08, rotate: 1 }}
              className="bg-[#14B8A6] text-black px-6 py-2 rounded-full text-sm font-bold shadow-[0_0_15px_rgba(20,184,166,0.4)] hover:shadow-[0_0_25px_rgba(20,184,166,0.8)] transition-all"
            >
              Sign Up
            </motion.button>
          </a>
        </div>
      </nav>

      {/* ================= SECTION 1 (HOME) ================= */}
      <section id="home" className="h-screen w-full relative">
        <div className="absolute inset-0">
          
          <div className="w-full h-full pointer-events-none">
            <Spline scene="https://prod.spline.design/k02TZsuEZZqvdLXf/scene.splinecode" style={{ width: '100%', height: '100%' }} />
          </div>
          
          {/* Real HTML Overlay Button to block and replace the baked Spline button */}
          <a 
            href="/login?mode=signup" 
            className="absolute z-50 left-[16.8%] bottom-[16%]"
          >
            <motion.button 
              type="button"
              whileHover={{ scale: 1.05, backgroundColor: "#064642" }}
              whileTap={{ scale: 0.95 }}
              className="bg-[#022a26] text-white px-[24px] py-[20px] rounded-[14px] font-bold text-[15px] tracking-widest shadow-[0_6px_25px_rgba(0,0,0,0.7)] border border-[#14B8A6]/20 flex items-center justify-center min-w-[170px] min-h-[64px]"
            >
              JOIN US NOW
            </motion.button>
          </a>

          {/* Watermark Cover Block */}
          <div className="absolute bottom-0 right-0 w-[200px] h-[80px] bg-[#050505] pointer-events-none rounded-tl-2xl z-[999]" />
        </div>
      </section>

      {/* ================= SECTION 2 (ABOUT) ================= */}
      <section id="about" className="min-h-screen flex items-center justify-between px-10">

        {/* LEFT TEXT */}
        <motion.div
          initial={{ opacity: 0, x: -80 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 1 }}
          className="max-w-2xl z-10 md:ml-12 lg:ml-24"
        >
          <h2 className="text-5xl md:text-6xl font-medium mb-8 leading-tight">
            Welcome to <br />
            <span className="text-[#14B8A6]">VitaScan</span>
          </h2>
          <div className="text-gray-400 leading-relaxed text-lg space-y-6">
            <p>
              VitaScan is an AI-driven health monitoring system that uses voice analysis to detect early signs of diseases. By combining advanced feature extraction (Librosa, OpenSMILE) with deep learning models like Wav2Vec 2.0, it analyzes vocal biomarkers and predicts potential health risks.
            </p>
            <p>
              The platform goes beyond prediction by tracking changes over time, identifying abnormal patterns, and providing early alerts. Designed for accessibility and real-time insights, VitaScan brings non-invasive, intelligent diagnostics to everyday users.
            </p>
          </div>

          <Link href="/learn-more">
            <button className="mt-10 px-8 py-3 bg-[#0B3B3C] hover:bg-[#115E59] text-white rounded-full font-medium transition-colors">
              Learn More
            </button>
          </Link>
        </motion.div>

        {/* RIGHT ROBOT */}
        <div className="w-[450px] h-[450px] md:w-[600px] md:h-[600px] lg:w-[750px] lg:h-[750px] relative flex items-center justify-center translate-x-6 lg:translate-x-16">
          {/* Synthetic Grid Background */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] md:w-[500px] md:h-[500px] lg:w-[600px] lg:h-[600px] bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-center bg-[size:48px_48px] rounded-2xl"></div>
          <div className="w-full h-full relative z-10 translate-x-8 md:translate-x-12 pointer-events-none">
            <Spline scene="https://prod.spline.design/jRONUHKEq7FZMQLg/scene.splinecode" />
          </div>
          {/* Watermark Cover Block */}
          <div className="absolute bottom-0 right-0 w-[220px] h-[80px] bg-[#050505] pointer-events-none rounded-tl-3xl z-[999]" />
        </div>
      </section>

      {/* ================= SECTION 3 (FEATURES) ================= */}
      <section id="features" className="py-32 px-6 md:px-10 relative z-10 bg-[#050505]">
        
        <div className="max-w-5xl mx-auto">
          <div className="flex flex-col items-center text-center mb-24">
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              className="px-5 py-1.5 border border-[#14B8A6]/30 rounded-full bg-[#14B8A6]/5 text-[#14B8A6] text-xs font-bold tracking-[0.3em] uppercase mb-6 shadow-[0_0_15px_rgba(20,184,166,0.15)] relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-[#14B8A6]/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              System Capabilities
            </motion.div>

            <motion.h2 
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-6xl md:text-8xl font-black mb-6 tracking-tighter"
            >
              <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-gray-200 to-gray-500">
                Core
              </span>{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-br from-[#14B8A6] via-[#2DD4BF] to-[#0F766E] drop-shadow-[0_0_25px_rgba(20,184,166,0.5)]">
                Features
              </span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-gray-400 text-lg md:text-xl font-light max-w-2xl text-center"
            >
              Advanced biometric diagnostics driven by cutting-edge neural algorithms.
            </motion.p>
            
            <motion.div 
              initial={{ width: 0 }}
              whileInView={{ width: "6rem" }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="h-1 bg-gradient-to-r from-transparent via-[#14B8A6] to-transparent mt-10 opacity-70 blur-[1px]"
            ></motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                id: "01",
                title: "Asthma Detection",
                desc: "Analyzes breathing patterns and voice irregularities to detect respiratory conditions like asthma. Identifies wheezing, airflow obstruction, and abnormal breathing signals using AI-driven audio analysis.",
                image: "/features/asthma.png",
                border: "border-cyan-500/20"
              },
              {
                id: "02",
                title: "Parkinson Detection",
                desc: "Detects early signs of Parkinson's disease using voice biomarkers such as tremors, pitch variation, and speech consistency. Uses AI models to analyze neurological irregularities in speech patterns.",
                image: "/features/parkinson.png",
                border: "border-purple-500/20"
              },
              {
                id: "03",
                title: "Healthy Status",
                desc: "Establishes a baseline of normal voice patterns to monitor overall health. Helps detect deviations over time and ensures stability in vocal biomarkers.",
                image: "/features/healthy2.png",
                border: "border-emerald-500/20"
              },
              {
                id: "04",
                title: "Depression Detection",
                desc: "Analyzes emotional and vocal patterns such as tone, pauses, and speech energy to detect mental health conditions like depression. Identifies subtle psychological indicators through AI.",
                image: "/features/depression.png",
                border: "border-indigo-500/20"
              },
            ].map((f, i) => {
              
              const isTypeA = i % 2 === 0;
              const isTypeB = i % 2 === 1;

              const TextContent = (
                <div className={`flex flex-col ${isTypeB ? 'mt-8 md:mt-12' : 'mb-8 md:mb-12'}`}>
                  <div 
                    className="text-7xl md:text-8xl font-black text-transparent mb-6 tracking-wide"
                    style={{ WebkitTextStroke: '2px rgba(255, 255, 255, 0.2)' }}
                  >
                    {f.id}
                  </div>
                  <h3 className="text-3xl md:text-4xl font-medium text-[#14B8A6] mb-6">
                    {f.title}
                  </h3>
                  <p className="text-gray-400 text-lg leading-relaxed">
                    {f.desc}
                  </p>
                </div>
              );

              const ImageContent = (
                <div className={`relative rounded-[2rem] overflow-hidden border border-white/5 ${f.border} shadow-lg aspect-square md:aspect-[4/3] w-full`}>
                  {/* Image is fully bright with no dark overlay whatsoever! */}
                  <Image src={f.image} alt={f.title} fill sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw" priority={true} className="object-cover hover:scale-105 transition-transform duration-700" />
                </div>
              );

              return (
                <motion.div 
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8 }}
                  viewport={{ once: true, margin: "-100px" }}
                  key={f.id} 
                  className="bg-[#0C0C0C] border border-white/5 flex flex-col rounded-[3rem] p-8 md:p-14 hover:border-white/10 transition-colors"
                >
                  {isTypeA ? <>{TextContent}{ImageContent}</> : <>{ImageContent}{TextContent}</>}
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ================= SECTION 4 (SPONSORSHIP) ================= */}
      <section id="sponsorship" className="min-h-[90vh] md:min-h-screen flex flex-col justify-start items-center text-center px-0 md:px-10 relative z-10 pt-16 pb-32 bg-[#050505] w-full overflow-hidden">
        
        <div className="relative z-20 bg-[#050505]/80 backdrop-blur-xl border border-white/10 px-8 md:px-20 py-8 md:py-10 rounded-[2.5rem] mt-10 shadow-3xl flex flex-col items-center">
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="text-5xl md:text-7xl font-bold mb-6 tracking-tight text-white"
          >
            Powered by <br className="md:hidden"/><span className="text-[#14B8A6] drop-shadow-[0_0_15px_rgba(20,184,166,0.5)]">Innovation</span>
          </motion.h2>

          <motion.p 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-gray-400 max-w-2xl text-lg md:text-xl"
          >
            Our innovation is supported by partners shaping the future of AI healthcare.
          </motion.p>
        </div>

        {/* THE EPIC PARTICLE TEXT MORPH ENGINE */}
        <ParticleSponsors />
      </section>

      {/* ================= SECTION 5 (CONTACT) ================= */}
      <section id="contact" className="min-h-screen flex flex-col justify-center items-center px-10 relative z-10 py-32 bg-[#050505] w-full overflow-hidden">
        
        <motion.h2 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="text-5xl md:text-7xl font-bold mb-16 text-white"
        >
          Contact <span className="text-[#14B8A6] drop-shadow-[0_0_15px_rgba(20,184,166,0.5)]">Us</span>
        </motion.h2>

        <form className="w-full max-w-xl flex flex-col gap-6 backdrop-blur-[30px] bg-white/[0.03] p-10 md:p-14 rounded-[2.5rem] border border-white/10 shadow-2xl relative overflow-hidden group">
          
          {/* Form internal neon glow effect */}
          <div className="absolute -inset-[1px] bg-gradient-to-b from-[#14B8A6]/20 to-[#0B3B3C]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-[2px] -z-10 rounded-[2.5rem]"></div>

          <div className="flex flex-col gap-3">
            <label className="text-xs text-[#14B8A6] uppercase tracking-widest font-semibold ml-2">Name</label>
            <input
              type="text"
              className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl focus:outline-none focus:border-[#14B8A6] focus:bg-white/[0.06] transition-all text-white placeholder-gray-600 focus:shadow-[0_0_15px_rgba(20,184,166,0.2)]"
              placeholder="John Doe"
            />
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-xs text-[#14B8A6] uppercase tracking-widest font-semibold ml-2">Email</label>
            <input
              type="email"
              className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl focus:outline-none focus:border-[#14B8A6] focus:bg-white/[0.06] transition-all text-white placeholder-gray-600 focus:shadow-[0_0_15px_rgba(20,184,166,0.2)]"
              placeholder="john@example.com"
            />
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-xs text-[#14B8A6] uppercase tracking-widest font-semibold ml-2">Message</label>
            <textarea
              rows={4}
              className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl focus:outline-none focus:border-[#14B8A6] focus:bg-white/[0.06] transition-all text-white placeholder-gray-600 resize-none focus:shadow-[0_0_15px_rgba(20,184,166,0.2)]"
              placeholder="How can we build the future together?"
            />
          </div>

          <Link href="/login?mode=signup" className="w-full mt-6 block">
            <motion.button 
              type="button"
              whileHover={{ scale: 1.02, backgroundColor: "#115E59" }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-[#0B3B3C] text-white py-4 rounded-2xl font-bold uppercase tracking-widest text-sm transition-all overflow-hidden relative border border-[#14B8A6]/20"
            >
              Join Us Now
            </motion.button>
          </Link>
        </form>

      </section>

    </main>
  );
}
