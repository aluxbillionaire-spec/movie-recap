<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UploadController;

Route::get('/', function () {
    return view('welcome');
});

// Dashboard route
Route::get('/dashboard', function () {
    return view('dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

// Uploads routes
Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/uploads', [UploadController::class, 'index'])->name('uploads.index');
    Route::post('/uploads', [UploadController::class, 'store'])->name('uploads.store');
});

// Downloads routes
Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/downloads', function () {
        return view('downloads.index');
    })->name('downloads.index');
});
