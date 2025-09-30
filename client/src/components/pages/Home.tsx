// Home.tsx - FULL UPDATED CODE
import { useMutation } from "@tanstack/react-query";
import api from "../../lib/axios/axios";
import { API_ROUTES } from "../../lib/api";
import { useRef, useState } from "react";
import { JsonViewer } from "../ui/home/JsonViewer";
import MessageBox from "../ui/home/MessageBox";
import React from 'react';

export default function Home() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [operationHistory, setOperationHistory] = useState<{
    id: string;
    timestamp: number;
    type: 'analysis' | 'render' | 'recreate';
    data: {
      knowYourKolam?: string;
      searchKolam?: string[];
      predictKolam?: string;
      renderedImage?: string;
      recreatedImage?: string;
    };
  }[]>([]);

  // API Mutations
  const knowYourKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post(API_ROUTES.KOLAM.KNOW_YOUR_KOLAM, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    }
  });

  const searchKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post(API_ROUTES.KOLAM.SEARCH, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data.matches;
    }
  });

  const predictKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post(API_ROUTES.KOLAM.PREDICT, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data.prediction;
    }
  });

  const renderKolamMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post(API_ROUTES.KOLAM.RENDER, data, {
        headers: { "Content-Type": "application/json" },
      });
      return res.data.file;
    },
    onSuccess: (renderedImage: string) => {
      const renderEntry = {
        id: Date.now().toString(),
        timestamp: Date.now(),
        type: 'render' as const,
        data: { renderedImage }
      };
      setOperationHistory(prev => [...prev, renderEntry]);

      const existing = localStorage.getItem("userKolams");
      const kolams = existing ? JSON.parse(existing) : [];
      kolams.unshift({
        id: Date.now(),
        title: `My Kolam #${kolams.length + 1}`,
        image: renderedImage.startsWith("http") ? renderedImage : `${import.meta.env.VITE_API_URL}/${renderedImage}`
      });
      localStorage.setItem("userKolams", JSON.stringify(kolams));
    }
  });

  // NEW: Kolam Re-creation Mutation
  const recreateKolamMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post(API_ROUTES.KOLAM.RECREATE, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data.recreatedImage;
    },
    onSuccess: (recreatedImage: string) => {
      const recreateEntry = {
        id: Date.now().toString(),
        timestamp: Date.now(),
        type: 'recreate' as const,
        data: { recreatedImage }
      };
      setOperationHistory(prev => [...prev, recreateEntry]);

      // Save to Community page
      const existing = localStorage.getItem("userKolams");
      const kolams = existing ? JSON.parse(existing) : [];
      kolams.unshift({
        id: Date.now(),
        title: `Recreated Kolam #${kolams.length + 1}`,
        image: recreatedImage.startsWith("http") ? recreatedImage : `${import.meta.env.VITE_API_URL}/${recreatedImage}`
      });
      localStorage.setItem("userKolams", JSON.stringify(kolams));
    }
  });

  const handleAnalyze = async () => {
    if (!file) return;

    try {
      const [knowResult, searchResult, predictResult] = await Promise.all([
        knowYourKolamMutation.mutateAsync(file),
        searchKolamMutation.mutateAsync(file),
        predictKolamMutation.mutateAsync(file)
      ]);

      const analysisEntry = {
        id: Date.now().toString(),
        timestamp: Date.now(),
        type: 'analysis' as const,
        data: {
          knowYourKolam: JSON.stringify(knowResult),
          searchKolam: searchResult,
          predictKolam: predictResult
        }
      };
      setOperationHistory(prev => ([...prev, analysisEntry]));

      renderKolamMutation.mutate(knowResult);

      setFile(null);
      setPreview(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (error) {
      console.error('Error analyzing kolam:', error);
    }
  };

  // NEW: Handle Recreate Kolam
  const handleRecreate = async () => {
    if (!file) return;

    try {
      await recreateKolamMutation.mutateAsync(file);
      
      setFile(null);
      setPreview(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (error) {
      console.error('Error recreating kolam:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPreview(URL.createObjectURL(file));
      setFile(file);
    }
  };

  return (
    <div className="grid grid-cols-5 h-full w-full">
      {/* main content */}
      <div className="col-span-4 p-8 w-full bg-gray-50 h-screen overflow-y-auto">
        <div className="flex flex-col gap-8 h-full">
          {(!operationHistory || operationHistory.length < 1) && (
            <div className="w-full h-full bg-white rounded-2xl p-4 flex items-center justify-center flex-col">
              <img src="/logo.webp" alt="" />
              <p className="text-gray-500">Upload a kolam image to get started</p>
            </div>
          )}
          {operationHistory.map(operation => {
            if (operation.type === 'analysis') {
              return (
                <div key={operation.id} className="flex flex-col gap-6">
                  <MessageBox width="fit-content" text={`Hmm, I think it's from the ${operation.data.predictKolam}, known as ${operation.data.predictKolam === "Maharastra" ? "Rangoli" : "Kolam"}.\nSimilar kolams found:`}>
                    <div className="grid grid-cols-3 gap-4">
                      {operation.data.searchKolam?.map(imgstr => (
                        <div key={imgstr} className="h-[200px] overflow-hidden aspect-square rounded-lg border border-gray-200">
                          <img
                            src={imgstr.startsWith('http') ? imgstr : `${import.meta.env.VITE_API_URL}/${imgstr}`}
                            alt="Similar kolam"
                            className="object-cover w-full h-full"
                          />
                        </div>
                      ))}
                    </div>
                  </MessageBox>
                  <MessageBox width="fit-content" text={`Mathematical representation of your kolam:`}>
                    <JsonViewer text={operation.data.knowYourKolam || ""} />
                  </MessageBox>
                </div>
              );
            } else if (operation.type === 'render') {
              return (
                <MessageBox key={operation.id} width="fit-content" text={`Here's the kolam rendered from analysis:`}>
                  {/* MODIFIED: Removed max-w-xl to allow the image to take up maximum available width */}
                  <div className="w-full rounded-lg border border-gray-200 bg-white p-4">
                    <img 
                      src={operation.data.renderedImage?.startsWith("http") ? operation.data.renderedImage : `${import.meta.env.VITE_API_URL}/${operation.data.renderedImage}`}
                      alt="Rendered kolam"
                      className="w-full h-auto object-contain" // Use h-auto and object-contain to ensure full image fit
                    />
                  </div>
                </MessageBox>
              );
            } else if (operation.type === 'recreate') {
              return (
                <MessageBox key={operation.id} width="fit-content" text={`Here's your recreated symmetric kolam:`}>
                  {/* MODIFIED: Better container for recreated image (Keeping max-w-xl here as it's a generated output, but updating the image style) */}
                  <div className="flex flex-col gap-4 max-w-xl"> 
                    {/* CHANGED: Removed fixed height and added responsive sizing with max height */}
                    <div className="w-full rounded-lg border border-gray-200 bg-white p-4">
                      <img
                        src={operation.data.recreatedImage?.startsWith("http") ? operation.data.recreatedImage : `${import.meta.env.VITE_API_URL}/${operation.data.recreatedImage}`}
                        alt="Recreated kolam"
                        className="w-full h-auto max-h-[400px] object-contain"
                      />
                    </div>
                    <div className="mt-4">
                      <a
                        href={operation.data.recreatedImage?.startsWith("http") ? operation.data.recreatedImage : `${import.meta.env.VITE_API_URL}/${operation.data.recreatedImage}`}
                        download="recreated_kolam.png"
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                      >
                        📥 Download Recreated Kolam
                      </a>
                    </div>
                  </div>
                </MessageBox>
              );
            }
            return null;
          })}
        </div>
      </div>

      {/* sidebar */}
      <div className="col-span-1 border-l border-gray-200 p-5">
        <input type="file" accept="image/*" ref={inputRef} onChange={handleFileChange} className="hidden" />
        
        {/* ORIGINAL IMAGE PREVIEW FIX: Removed aspect-square to allow flexible size */}
        <div
          className="w-full flex flex-col items-center justify-center border-2 border-dashed border-gray-400 rounded-2xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition overflow-hidden"
          onClick={() => inputRef.current?.click()}
        >
          {preview ? <img src={preview} alt="Preview" className="object-contain w-full h-full" /> : (
            <>
              <span className="text-4xl text-gray-500">+</span>
              <p className="text-gray-600 mt-2">Upload Photo</p>
            </>
          )}
        </div>

        {file && (
          <div className="flex flex-col gap-2 mt-4">
            <button
              className="px-4 py-2 text-primary border-1 font-semibold border-primary rounded-lg bg-white hover:bg-blue-50 transition-colors"
              onClick={handleAnalyze}
              disabled={knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending || renderKolamMutation.isPending}
            >
              {(knowYourKolamMutation.isPending || searchKolamMutation.isPending || predictKolamMutation.isPending || renderKolamMutation.isPending) ? "Processing..." : "Analyze & Render"}
            </button>
            
            {/* NEW: Recreate Kolam Button */}
            <button
              className="px-4 py-2 text-green-600 border-1 font-semibold border-green-600 rounded-lg bg-white hover:bg-green-50 transition-colors"
              onClick={handleRecreate}
              disabled={recreateKolamMutation.isPending}
            >
              {recreateKolamMutation.isPending ? "Recreating..." : "Recreate Symmetric Kolam"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}