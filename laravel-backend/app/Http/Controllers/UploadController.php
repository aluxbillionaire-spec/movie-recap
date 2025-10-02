<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use App\Services\MovieRecapService;
use App\Models\Project;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Auth;

class UploadController extends Controller
{
    protected MovieRecapService $movieRecapService;

    public function __construct(MovieRecapService $movieRecapService)
    {
        $this->movieRecapService = $movieRecapService;
    }

    /**
     * Show the upload form
     */
    public function index()
    {
        return view('uploads.index');
    }

    /**
     * Store the uploaded files
     */
    public function store(Request $request): RedirectResponse
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'movie_file' => 'required|file|mimes:mp4,avi,mov,mkv|max:10240000', // 10GB max
            'script_file' => 'nullable|file|mimes:txt,doc,docx,pdf|max:1024000', // 1GB max
        ]);

        // Create a project for this upload
        $project = Project::create([
            'user_id' => Auth::id(),
            'tenant_id' => 'default-tenant-id', // In a real app, you would get this from the user's tenant
            'title' => $request->title,
            'description' => $request->description,
            'status' => 'active',
        ]);

        // Handle movie file upload
        if ($request->hasFile('movie_file')) {
            $movieFile = $request->file('movie_file');

            // For files under 100MB, we can use direct upload
            if ($movieFile->getSize() < 100 * 1024 * 1024) {
                $response = $this->movieRecapService->directUpload([
                    'project_id' => $project->id,
                    'file_type' => 'video',
                ], $movieFile);

                if (!$response) {
                    return redirect()->back()->with('error', 'Failed to upload movie file.');
                }
            } else {
                // For larger files, use resumable upload
                $initResponse = $this->movieRecapService->initializeUpload([
                    'project_id' => $project->id,
                    'file_type' => 'video',
                    'filename' => $movieFile->getClientOriginalName(),
                    'file_size' => $movieFile->getSize(),
                    'content_type' => $movieFile->getMimeType(),
                ]);

                if (!$initResponse) {
                    return redirect()->back()->with('error', 'Failed to initialize movie upload.');
                }

                // In a real implementation, you would handle the resumable upload process
                // This is a simplified version that just shows the concept
                // $uploadId = $initResponse['upload_id'];
                // $uploadUrl = $initResponse['upload_url'];
                // ... handle chunked upload ...
                // $completeResponse = $this->movieRecapService->completeUpload($uploadId);
            }
        }

        // Handle script file upload
        if ($request->hasFile('script_file')) {
            $scriptFile = $request->file('script_file');

            // For files under 100MB, we can use direct upload
            if ($scriptFile->getSize() < 100 * 1024 * 1024) {
                $response = $this->movieRecapService->directUpload([
                    'project_id' => $project->id,
                    'file_type' => 'script',
                ], $scriptFile);

                if (!$response) {
                    return redirect()->back()->with('error', 'Failed to upload script file.');
                }
            } else {
                // For larger files, use resumable upload
                $initResponse = $this->movieRecapService->initializeUpload([
                    'project_id' => $project->id,
                    'file_type' => 'script',
                    'filename' => $scriptFile->getClientOriginalName(),
                    'file_size' => $scriptFile->getSize(),
                    'content_type' => $scriptFile->getMimeType(),
                ]);

                if (!$initResponse) {
                    return redirect()->back()->with('error', 'Failed to initialize script upload.');
                }

                // In a real implementation, you would handle the resumable upload process
                // This is a simplified version that just shows the concept
                // $uploadId = $initResponse['upload_id'];
                // $uploadUrl = $initResponse['upload_url'];
                // ... handle chunked upload ...
                // $completeResponse = $this->movieRecapService->completeUpload($uploadId);
            }
        }

        return redirect()->route('dashboard')->with('success', 'Files uploaded successfully! Processing will begin shortly.');
    }
}
