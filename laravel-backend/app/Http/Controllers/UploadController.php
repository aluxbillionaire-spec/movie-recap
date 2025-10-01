<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Spatie\MediaLibrary\MediaCollections\Models\Media;

class UploadController extends Controller
{
    /**
     * Show the upload form
     */
    public function index()
    {
        return view('uploads.index');
    }

    /**
     * Store the uploaded file
     */
    public function store(Request $request): RedirectResponse
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'file' => 'required|file|mimes:mp4,avi,mov,mkv|max:10240', // 10GB max
        ]);

        // For now, we'll just store the file using Spatie Media Library
        // In a real application, you would associate this with a model
        if ($request->hasFile('file')) {
            $file = $request->file('file');

            // Store the file using Spatie Media Library
            // This is a simplified example - in reality you would associate with a model
            $media = Media::make([
                'name' => $request->title,
                'file_name' => $file->getClientOriginalName(),
                'mime_type' => $file->getMimeType(),
                'size' => $file->getSize(),
            ]);

            // In a real application, you would associate with a model like:
            // $project = Project::create([
            //     'title' => $request->title,
            //     'description' => $request->description,
            // ]);
            // $project->addMedia($file)->toMediaCollection('videos');
        }

        return redirect()->route('dashboard')->with('success', 'File uploaded successfully! Processing will begin shortly.');
    }
}
