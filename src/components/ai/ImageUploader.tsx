import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Camera, Upload, X, AlertCircle, CheckCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ImageUploaderProps {
  onImagesSelected: (images: File[]) => void;
  maxImages?: number;
  className?: string;
}

export default function ImageUploader({
  onImagesSelected,
  maxImages = 5,
  className = "",
}: ImageUploaderProps) {
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    processFiles(Array.from(files));
  };

  const processFiles = (files: File[]) => {
    setError(null);

    // Filter for image files only
    const imageFiles = files.filter(
      (file) =>
        file.type.startsWith("image/jpeg") ||
        file.type.startsWith("image/png") ||
        file.type.startsWith("image/heic") ||
        file.type.startsWith("image/heif"),
    );

    if (imageFiles.length === 0) {
      setError("Please select valid image files (JPG, PNG, HEIC/HEIF).");
      return;
    }

    // Check file size (max 10MB per file)
    const validSizeFiles = imageFiles.filter(
      (file) => file.size <= 10 * 1024 * 1024,
    );
    if (validSizeFiles.length < imageFiles.length) {
      setError("Some images exceed the 10MB size limit and were excluded.");
    }

    // Check if adding these files would exceed max images
    if (selectedImages.length + validSizeFiles.length > maxImages) {
      setError(`You can upload a maximum of ${maxImages} images.`);
      const allowedNewFiles = validSizeFiles.slice(
        0,
        maxImages - selectedImages.length,
      );
      setSelectedImages((prev) => [...prev, ...allowedNewFiles]);
      onImagesSelected([...selectedImages, ...allowedNewFiles]);
      return;
    }

    setSelectedImages((prev) => [...prev, ...validSizeFiles]);
    onImagesSelected([...selectedImages, ...validSizeFiles]);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const removeImage = (index: number) => {
    const newImages = [...selectedImages];
    newImages.splice(index, 1);
    setSelectedImages(newImages);
    onImagesSelected(newImages);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center ${
          dragActive ? "border-primary bg-primary/5" : "border-gray-300"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="rounded-full bg-primary/10 p-3">
            <Camera className="h-8 w-8 text-primary" />
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">Upload Product Images</h3>
            <p className="text-sm text-gray-500">
              Drag and drop your images here, or click to browse
            </p>
            <p className="text-xs text-gray-500">
              Supports JPG, PNG, HEIF/HEIC (max {maxImages} images, 10MB each)
            </p>
          </div>
          <Label htmlFor="image-upload" className="cursor-pointer">
            <div className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium flex items-center">
              <Upload className="mr-2 h-4 w-4" />
              Browse Files
            </div>
            <Input
              id="image-upload"
              type="file"
              accept="image/jpeg,image/png,image/heic,image/heif"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
          </Label>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {selectedImages.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            Selected Images ({selectedImages.length}/{maxImages})
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {selectedImages.map((file, index) => (
              <Card key={index} className="overflow-hidden relative group">
                <CardContent className="p-0">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Selected ${index + 1}`}
                    className="w-full h-32 object-cover"
                  />
                  <Button
                    variant="destructive"
                    size="icon"
                    className="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => removeImage(index)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                  <div className="p-2 text-xs truncate">{file.name}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
