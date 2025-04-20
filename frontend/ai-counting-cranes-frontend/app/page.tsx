"use client"

import type React from "react"

import { useState } from "react"
import { Upload, ImagePlus, Loader2, CheckCircle2, AlertCircle, Camera, RefreshCw } from "lucide-react"
import Image from "next/image"
import { motion, AnimatePresence } from "framer-motion"
import confetti from "canvas-confetti"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"

export default function ObjectCounter() {
  const [image, setImage] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<{ count: number; objects: string[] } | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const { toast } = useToast()

  // Handle drag events
  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0])
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    handleFiles(file)
  }

  const handleFiles = (file: File) => {
    // Check if the file is an image
    if (!file.type.startsWith("image/")) {
      toast({
        title: "Invalid file type",
        description: "Please upload an image file.",
        variant: "destructive",
      })
      return
    }

    setFile(file)
    const reader = new FileReader()
    reader.onload = () => {
      setImage(reader.result as string)
      setResults(null) // Reset results when new image is uploaded
    }
    reader.readAsDataURL(file)
  }

  const processImage = async () => {
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file); // 'file' must match FastAPI param
  
    try {
      const res = await fetch("http://localhost:8000/predict-image/", {
        method: "POST",
        body: formData,
      });
  
      if (!res.ok) throw new Error("Backend error");
  
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setImage(url); // display returned image
    } catch (err) {
      console.error("Inference failed:", err);
    }
  };
  

  const resetForm = () => {
    setImage(null)
    setFile(null)
    setResults(null)
    setProgress(0)
  }

  // Object icons mapping
  const objectIcons: Record<string, React.ReactNode> = {
    person: "👤",
    car: "🚗",
    dog: "🐕",
    bicycle: "🚲",
    tree: "🌳",
    bird: "🐦",
  }

  return (
<div
    className="min-h-screen bg-cover bg-center"
    style={{ backgroundImage: `url('/background_image.jpg')` }}
  >    <div className="min-h-screen backdrop-blur-sm bg-white/70">
      <div className="container mx-auto py-10 px-4 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-rose-500 to-purple-600 bg-clip-text text-transparent">
            Sandhill Crane Object Detector
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Upload an image to count and identify Sandhill Cranes/Duck Geese using machine learning!
          </p>
        </motion.div>


        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="w-full overflow-hidden border-2 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-rose-50 to-purple-50 dark:from-rose-950/20 dark:to-purple-950/20">
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-rose-500" />
                Image Analysis
              </CardTitle>
              <CardDescription>
                Upload an image to analyze. The model will count and identify objects in the image.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 p-6">
              <AnimatePresence mode="wait">
                {!image ? (
                  <motion.div
                    key="upload"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
                      dragActive
                        ? "border-rose-400 bg-rose-50 dark:border-rose-500 dark:bg-rose-950/20"
                        : "border-gray-300 hover:border-gray-400 dark:border-gray-700 dark:hover:border-gray-600"
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <div className="flex flex-col items-center justify-center gap-4">
                      <motion.div
                        animate={{
                          scale: dragActive ? 1.1 : 1,
                          y: dragActive ? -10 : 0,
                        }}
                        transition={{ type: "spring", stiffness: 400, damping: 10 }}
                      >
                        <div className="w-24 h-24 rounded-full bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center mb-2">
                          <ImagePlus className="h-12 w-12 text-rose-500" />
                        </div>
                      </motion.div>
                      <div>
                        <p className="text-lg font-medium mb-1">Drag and drop an image here</p>
                        <p className="text-sm text-muted-foreground">or click to browse your files</p>
                      </div>
                      <div className="mt-4">
  <input
    type="file"
    id="image-upload"
    accept="image/*"
    onChange={handleImageUpload}
    style={{ display: "none" }}
  />
  <button
    onClick={() => document.getElementById("image-upload")?.click()}
    className="bg-rose-500 text-white font-bold px-4 py-2 rounded hover:bg-rose-600"
  >
    Select Image
  </button>
</div>

                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="preview"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                  >
                    <motion.div
                      initial={{ scale: 0.9 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 300, damping: 25 }}
                      className="relative aspect-video overflow-hidden rounded-lg border bg-muted shadow-md"
                    >
                      <Image src={image || "/placeholder.svg"} alt="Uploaded image" fill className="object-contain" />
                      {isProcessing && (
                        <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-white p-6">
                          <Loader2 className="h-12 w-12 animate-spin mb-4" />
                          <h3 className="text-xl font-medium mb-2">Analyzing Image</h3>
                          <p className="text-sm text-gray-300 mb-4 text-center">
                            Our AI is identifying and counting objects in your image
                          </p>
                          <div className="w-full max-w-md">
                            <Progress value={progress} className="h-2 bg-gray-700" />
                            <p className="text-right text-sm mt-1">{progress}%</p>
                          </div>
                        </div>
                      )}
                    </motion.div>

                    <div className="flex flex-wrap gap-2">
                      <Button onClick={processImage} disabled={isProcessing} className="relative overflow-hidden group">
                        <span className="absolute inset-0 bg-gradient-to-r from-rose-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                        {isProcessing ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin relative z-10" />
                            <span className="relative z-10">Processing...</span>
                          </>
                        ) : (
                          <>
                            <span className="relative z-10">Process Image</span>
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={resetForm} disabled={isProcessing}>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Upload New Image
                      </Button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {results && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Separator className="my-6" />
                    <div className="space-y-6">
                      <h3 className="text-xl font-medium flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Analysis Results
                      </h3>
                      <div className="grid gap-6 md:grid-cols-2">
                        <motion.div
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <Card className="overflow-hidden border-2 h-full">
                            <CardHeader className="bg-gradient-to-r from-rose-50 to-purple-50 dark:from-rose-950/20 dark:to-purple-950/20 pb-2">
                              <CardTitle className="text-4xl font-bold text-center bg-gradient-to-r from-rose-500 to-purple-600 bg-clip-text text-transparent">
                                {results.count}
                              </CardTitle>
                              <CardDescription className="text-center text-base">
                                Total Objects Detected
                              </CardDescription>
                            </CardHeader>
                            <CardContent className="pt-6">
                              <div className="aspect-square max-w-[180px] mx-auto relative">
                                <div className="absolute inset-0 rounded-full bg-gradient-to-r from-rose-100 to-purple-100 dark:from-rose-900/30 dark:to-purple-900/30 animate-pulse"></div>
                                <div className="absolute inset-2 rounded-full bg-white dark:bg-gray-950 flex items-center justify-center">
                                  <span className="text-6xl">{results.count > 10 ? "🔍" : "🎯"}</span>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>

                        <motion.div
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: 0.3 }}
                        >
                          <Card className="overflow-hidden border-2 h-full">
                            <CardHeader className="bg-gradient-to-r from-rose-50 to-purple-50 dark:from-rose-950/20 dark:to-purple-950/20 pb-2">
                              <CardTitle className="text-xl">Detected Objects</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-6">
                              <div className="grid grid-cols-2 gap-3">
                                {results.objects.map((object, index) => (
                                  <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 + index * 0.1 }}
                                    className="bg-gradient-to-r from-rose-100 to-purple-100 dark:from-rose-900/30 dark:to-purple-900/30 p-4 rounded-lg flex items-center gap-3"
                                  >
                                    <div className="text-2xl">{objectIcons[object] || "🔍"}</div>
                                    <div className="font-medium capitalize">{object}</div>
                                  </motion.div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
            <CardFooter className="text-sm text-muted-foreground bg-gradient-to-r from-rose-50 to-purple-50 dark:from-rose-950/20 dark:to-purple-950/20 border-t">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
                For best results, use clear images with distinct objects.
              </div>
            </CardFooter>
          </Card>
        </motion.div>
      </div>
    </div>
    </div>
  )
}
