import ffmpeg

ffmpeg.input(r'C:\Users\yasmi\Documents\dash\videosnew\apres-midi\pile.MOV').output('pile.mp4', vcodec='libx264', acodec='aac').run()
