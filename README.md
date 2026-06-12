# FFmpeg Chapter Marker Tool

This tool helps you add chapter markers to an MP4 file using FFmpeg and a text file.

# Text file format

The CHAPTERS_SOURCE file should have one chapter on each line, in the format:

> h:mm:ss Chapter Title

(for example, `0:00:00 Opening Credits`, or `1:23:45 Closing Credits`)

The final line in the file must be set to the length of the video and given the chapter title "END".
