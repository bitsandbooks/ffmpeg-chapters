# FFmpeg Chapter Marker Tool

This tool helps you add chapter markers to an MP4 file using FFmpeg and a text file. I currently use it for adding chapters to a video series I subscribe to, whose long episodes currently have no chapter markers. 😖

## How it works

1. The container reads the input file from the `data` volume and generates a basic metadata file in `data/headers` (creating the folder if it doesn't exist).
2. It reads `chapters.txt`, a simple list of chapter markers, and appends them to the metadata file.
3. It moves the original video file to `data/originals`, appending `-nochapters` to the filename (before the extension) for safety's sake.
4. It writes a new video file with chapter markers, using the same file name as the original, to `data/output`.

## Data Folder

The data folder is where your (chapter-less) "input" video lives. This folder should be mounted at `/data` inside the container.

## `chapters.txt`

`chapters.txt` is a text file containing chapter markers. You may have an arbitrary number of chapters, one on each line of the file, in the format:

> h:mm:ss Chapter Title

(for example, `0:00:00 Opening Credits`, or `1:23:45 Closing Credits`)

The final line in the file *must* be set to the length of the video and given the chapter title "END".

## Usage

Run a temporary Docker container to process a file in the current folder, like so:

    docker run \
           --rm \
           -v "$(pwd):/data" \
           -w /data \
           makechapters:late \
           my_video.m4v

This will result in a new file with the same name in the `output` folder. The original is backed up in `originals` under the name `my_video-nochapters.m4v`.
