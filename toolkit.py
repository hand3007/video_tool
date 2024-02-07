import os
import numpy as np
import argparse

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from pytube import Playlist, YouTube
from pytube.exceptions import VideoUnavailable
from concurrent.futures import ThreadPoolExecutor


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_time(input_str):
    return int(input_str[:input_str.index(":")]), int(input_str[input_str.index(":") + 1:])


def get_intro_path(input_int):
    current_directory = os.getcwd()
    converted_directory = current_directory.replace("\\", "/")
    return f"{converted_directory}/intros/{input_int}.mp4"


class Movie:
    @staticmethod
    def _get_subclip_volume(subclip, second, interval):
        cut = subclip.subclip(second, second + interval).audio.to_soundarray(fps=44100)
        return np.sqrt(((1.0 * cut) ** 2).mean())

    @staticmethod
    def _float_to_srt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:02d}"

    @staticmethod
    def get_audio(input_video_file_clip, filename):
        audio_file_name = f"{filename}_audio.wav"

        if os.path.exists(audio_file_name):
            os.remove(audio_file_name)

        input_video_file_clip.audio.write_audiofile(audio_file_name, codec="pcm_s161e")
        return audio_file_name

    @staticmethod
    def save_video(**kwargs):
        filename = kwargs["filename"]
        input_video_file_clip = kwargs["input_video_file_clip"]

        clip_name = f"{filename}_EDITED.mp4"

        input_video_file_clip.write_videofile(clip_name, audio_codec="aac")
        kwargs["clips_name"] = clip_name
        return kwargs

    @staticmethod
    def add_one_audio_to_video(input_audio, input_video):
        parser = argparse.ArgumentParser(description="Python script to add audio to video clip")
        parser.add_argument("-v", "--video-file", help="Target video file")
        parser.add_argument("-a", "--audio-file", help="Target audio file to embed with the video")
        parser.add_argument("-s", "--start", help="Start duration of the audio file, default is 0", default=0, type=int)
        parser.add_argument("-e", "--end",
                            help="The end duration of the audio file, default is the length of the video file",
                            type=int)
        parser.add_argument("-c", "--composite", help="Whether to add to the existing audio in the video",
                            action="store_true", default=False)
        parser.add_argument("-f", "--volume-factor", type=float, default=1.0,
                            help="The volume factor to multiply by the volume of the audio file, 1 means no change, "
                                 "below 1 will decrease volume, above will increase.")
        # parse the arguments
        args = parser.parse_args()
        # video_file = args.video_file
        # audio_file = args.audio_file
        start = args.start
        end = args.end
        composite = args.composite
        volume_factor = args.volume_factor
        print(vars(args))
        video_clip = VideoFileClip(input_video)
        audio_clip = AudioFileClip(input_audio)

        # use the volume factor to increase/decrease volume
        audio_clip = audio_clip.volumex(volume_factor)

        # if end is not set, use video clip's end
        if not end:
            end = video_clip.end
        # make sure audio clip is less than video clip in duration
        # setting the start & end of the audio clip to `start` and `end` paramters
        audio_clip = audio_clip.subclip(start, end)

        # composite with the existing audio in the video if composite parameter is set
        if composite:
            final_audio = CompositeAudioClip([video_clip.audio, audio_clip])
        else:
            final_audio = audio_clip
        # add the final audio to the video
        final_clip = video_clip.set_audio(final_audio)

        # save the final clip
        final_clip.write_videofile(f"{input_video[:-4]}_final.mp4")

    @staticmethod
    def add_one_audio_to_many_videos(input_audio, input_videos):
        max_videos = list(chunks(input_videos, len(input_videos))) if len(input_videos) < 6 \
            else list(chunks(input_videos, 5))
        for max_video in max_videos:
            with ThreadPoolExecutor(max_workers=len(max_video)) as executor:
                results = [executor.submit(Movie.add_one_audio_to_video, input_audio, video)
                           for video in max_video]

    @staticmethod
    def remove_audio(input_video):
        final_video = VideoFileClip(input_video).without_audio()
        final_video.write_videofile(f"{input_video[:-4]}_final.mp4")

    @staticmethod
    def remove_audio_many(input_videos):
        max_videos = list(chunks(input_videos, len(input_videos))) if len(input_videos) < 6 \
            else list(chunks(input_videos, 5))
        for max_video in max_videos:
            with ThreadPoolExecutor(max_workers=len(max_video)) as executor:
                results = [executor.submit(Movie.remove_audio, video) for video in max_video]

    @staticmethod
    # cut video, x1, x2 expression: (hour, min, second)
    def sub_clip(input_video, x1, x2):
        clip = VideoFileClip(input_video)
        clip1 = clip.subclip(x1, x2)
        clip1.write_videofile(f"{input_video[:-4]}_final.mp4", codec='libx264')

    @staticmethod
    def sub_clip_many(list_input_videos, x1, x2):
        max_videos = list(chunks(list_input_videos, len(list_input_videos))) if len(list_input_videos) < 6 \
            else list(chunks(list_input_videos), 5)
        for max_video in max_videos:
            with ThreadPoolExecutor(max_workers=len(max_video)) as executor:
                results = [executor.submit(Movie.sub_clip, video, x1, x2) for video in max_video]

    @staticmethod
    def overlay_text(video_path, text, colour, size, bg):
        # Load the video clip
        video_clip = VideoFileClip(video_path)
        # Create a TextClip with the desired text
        txt_clip = TextClip(text, fontsize=size, color=colour, bg_color=bg)
        # Say that you want it to appear 10s at the center of the screen
        txt_clip = txt_clip.set_pos('top').set_duration(10)
        # Overlay the text clip on the first video clip
        video_with_text = CompositeVideoClip([video_clip, txt_clip])
        # Write the result to a file (many options available !)
        video_with_text.write_videofile(f"{video_path[:-4]}_final.mp4", codec='libx264', audio_codec='aac',
                                        temp_audiofile='temp-audio.m4a', remove_temp=True)

    @staticmethod
    # Insert frame to video
    def insert_frame(video_path, image_path, output_path):
        # Load the video clip
        video_clip = VideoFileClip(video_path)

        # Load the image to be inserted as a frame
        frame_image = ImageClip(image_path, duration=video_clip.duration)

        # Overlay the image on the video
        video_with_frame = CompositeVideoClip([video_clip, frame_image.set_pos('center')])

        # Write the result to a file
        video_with_frame.write_videofile(output_path, codec='libx264', audio_codec='aac',
                                         temp_audiofile='temp-audio.m4a', remove_temp=True)

    @staticmethod
    # rotate video
    def rotate(input_video, x):
        clip = VideoFileClip(input_video).rotate(x)
        clip.ipython_display(width=280)

    @staticmethod
    # mp4 to mp3 function
    def mp4_to_mp3(input_mp4):
        video = VideoFileClip(input_mp4)
        video.audio.write_audiofile('mp3.mp3')

    @staticmethod
    # concatenate video
    def concatenate(video_clip_paths, tree_view_path, method="compose"):
        """Concatenates several video files into one video file
        and save it to `output_path`. Note that extension (mp4, etc.) must be added to `output_path`
        `method` can be either 'compose' or 'reduce':
            `reduce`: Reduce the quality of the video to the lowest quality on the list of `video_clip_paths`.
            `compose`: type help(concatenate_videoclips) for the info"""
        # create VideoFileClip object for each video file
        clips = [VideoFileClip(c) for c in video_clip_paths]
        if method == "reduce":
            # calculate minimum width & height across all clips
            min_height = min([c.h for c in clips])
            min_width = min([c.w for c in clips])
            # resize the videos to the minimum
            clips = [c.resize(newsize=(min_width, min_height)) for c in clips]
            # concatenate the final
            # video
            final_clip = concatenate_videoclips(clips)
        elif method == "compose":
            # concatenate the final video with the compose method provided by moviepy
            final_clip = concatenate_videoclips(clips, method="compose")
        # write the output video file
        final_clip.write_videofile(f"{tree_view_path[:-4]}_final.mp4")

    @staticmethod
    def concatenate_many(list_input_videos):
        max_videos = list(chunks(list_input_videos, len(list_input_videos))) if len(list_input_videos) < 6 \
            else list(chunks(list_input_videos), 5)
        for max_video in max_videos:
            with ThreadPoolExecutor(max_workers=len(max_video)) as executor:
                results = [executor.submit(Movie.concatenate, video) for video in max_video]

    @staticmethod
    # add intro
    def add_intro(intro_link, selected_video, out_video):
        out_video = concatenate_videoclips(intro_link, selected_video)
        out_video.write_videofile('/videos/insert_path_here.mp4')

    @staticmethod
    # download list video from youtube
    def download_videos(link):
        playlist_url = link
        p = Playlist(playlist_url)
        for url in p.video_urls:
            try:
                yt = YouTube(url)
            except VideoUnavailable:
                print(f'Video {url} is unavailable, skipping.')
            else:
                print(f'Download video: {url}')
                yt.streams.get_highest_resolution().download()
                # yt.streams.get_by_resolution(720).download()

    @staticmethod
    # download one video from youtube
    def download_video(link):
        youtube_object = YouTube(link)
        youtube_object = youtube_object.streams.get_highest_resolution()
        try:
            youtube_object.download()
        except Exception as e:
            print(e)
            print("An error has occurred")
        print("Download is completed successfully")
