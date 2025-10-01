<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Dashboard') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <!-- Upload Card -->
                        <div class="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
                            <div class="flex items-center">
                                <div class="rounded-full bg-white/20 p-3 mr-4">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold">Upload Files</h3>
                                    <p class="text-sm opacity-80">Upload your movie files for processing</p>
                                </div>
                            </div>
                            <a href="{{ route('uploads.index') }}" class="mt-4 inline-block bg-white text-blue-600 font-medium py-2 px-4 rounded-lg hover:bg-gray-100 transition duration-200">
                                Upload Now
                            </a>
                        </div>

                        <!-- Processing Card -->
                        <div class="bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
                            <div class="flex items-center">
                                <div class="rounded-full bg-white/20 p-3 mr-4">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold">Processing</h3>
                                    <p class="text-sm opacity-80">View your processing jobs</p>
                                </div>
                            </div>
                            <a href="#" class="mt-4 inline-block bg-white text-amber-600 font-medium py-2 px-4 rounded-lg hover:bg-gray-100 transition duration-200">
                                View Jobs
                            </a>
                        </div>

                        <!-- Download Card -->
                        <div class="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg p-6 text-white">
                            <div class="flex items-center">
                                <div class="rounded-full bg-white/20 p-3 mr-4">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold">Downloads</h3>
                                    <p class="text-sm opacity-80">Download your processed files</p>
                                </div>
                            </div>
                            <a href="{{ route('downloads.index') }}" class="mt-4 inline-block bg-white text-green-600 font-medium py-2 px-4 rounded-lg hover:bg-gray-100 transition duration-200">
                                Download Files
                            </a>
                        </div>
                    </div>

                    <!-- Stats Section -->
                    <div class="mt-8">
                        <h3 class="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h3>
                        <div class="bg-gray-50 rounded-lg p-6">
                            <p class="text-gray-600">No recent activity. Upload a file to get started!</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>
