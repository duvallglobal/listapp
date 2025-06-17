
import { supabase } from '@/lib/supabase';
import { v4 as uuidv4 } from 'uuid';

export interface ImageUploadOptions {
  bucket: string;
  folder?: string;
  compress?: boolean;
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
}

export interface UploadedImage {
  id: string;
  url: string;
  publicUrl: string;
  path: string;
  size: number;
  type: string;
}

class ImageService {
  private defaultOptions: ImageUploadOptions = {
    bucket: 'analysis-images',
    folder: 'uploads',
    compress: true,
    maxWidth: 1920,
    maxHeight: 1080,
    quality: 0.85
  };

  /**
   * Compress and resize image before upload
   */
  private async compressImage(
    file: File, 
    options: ImageUploadOptions
  ): Promise<File> {
    if (!options.compress) return file;

    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Calculate new dimensions
        let { width, height } = img;
        const maxWidth = options.maxWidth || this.defaultOptions.maxWidth!;
        const maxHeight = options.maxHeight || this.defaultOptions.maxHeight!;

        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }
        if (height > maxHeight) {
          width = (width * maxHeight) / height;
          height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;

        // Draw and compress
        ctx?.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressedFile = new File([blob], file.name, {
                type: file.type,
                lastModified: Date.now()
              });
              resolve(compressedFile);
            } else {
              resolve(file);
            }
          },
          file.type,
          options.quality || this.defaultOptions.quality
        );
      };

      img.src = URL.createObjectURL(file);
    });
  }

  /**
   * Upload single image to Supabase Storage
   */
  async uploadImage(
    file: File, 
    userId: string, 
    options: Partial<ImageUploadOptions> = {}
  ): Promise<UploadedImage> {
    const opts = { ...this.defaultOptions, ...options };
    
    try {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        throw new Error('File must be an image');
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('File size must be less than 10MB');
      }

      // Compress image if needed
      const processedFile = await this.compressImage(file, opts);

      // Generate unique filename
      const fileExt = file.name.split('.').pop();
      const fileName = `${uuidv4()}.${fileExt}`;
      const filePath = `${opts.folder}/${userId}/${fileName}`;

      // Upload to Supabase Storage
      const { data, error } = await supabase.storage
        .from(opts.bucket)
        .upload(filePath, processedFile, {
          cacheControl: '3600',
          upsert: false
        });

      if (error) {
        throw new Error(`Upload failed: ${error.message}`);
      }

      // Get public URL
      const { data: urlData } = supabase.storage
        .from(opts.bucket)
        .getPublicUrl(filePath);

      return {
        id: fileName.split('.')[0],
        url: urlData.publicUrl,
        publicUrl: urlData.publicUrl,
        path: filePath,
        size: processedFile.size,
        type: file.type
      };

    } catch (error) {
      console.error('Image upload error:', error);
      throw error;
    }
  }

  /**
   * Upload multiple images
   */
  async uploadMultipleImages(
    files: File[], 
    userId: string, 
    options: Partial<ImageUploadOptions> = {}
  ): Promise<UploadedImage[]> {
    const uploadPromises = files.map(file => 
      this.uploadImage(file, userId, options)
    );

    try {
      return await Promise.all(uploadPromises);
    } catch (error) {
      console.error('Multiple image upload error:', error);
      throw error;
    }
  }

  /**
   * Delete image from storage
   */
  async deleteImage(path: string, bucket: string = 'analysis-images'): Promise<void> {
    try {
      const { error } = await supabase.storage
        .from(bucket)
        .remove([path]);

      if (error) {
        throw new Error(`Delete failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Image delete error:', error);
      throw error;
    }
  }

  /**
   * Get signed URL for private images
   */
  async getSignedUrl(
    path: string, 
    expiresIn: number = 3600, 
    bucket: string = 'analysis-images'
  ): Promise<string> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .createSignedUrl(path, expiresIn);

      if (error) {
        throw new Error(`Signed URL generation failed: ${error.message}`);
      }

      return data.signedUrl;
    } catch (error) {
      console.error('Signed URL error:', error);
      throw error;
    }
  }

  /**
   * List user's uploaded images
   */
  async listUserImages(
    userId: string, 
    bucket: string = 'analysis-images'
  ): Promise<any[]> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .list(`uploads/${userId}`, {
          limit: 100,
          offset: 0
        });

      if (error) {
        throw new Error(`List images failed: ${error.message}`);
      }

      return data || [];
    } catch (error) {
      console.error('List images error:', error);
      throw error;
    }
  }
}

export const imageService = new ImageService();
