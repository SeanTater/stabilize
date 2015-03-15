The plan:
> Compensate for panning, rotation, zoom and perhaps minor perspective changes in a video.

The progress:
> Video in most formats (e.g. what avcodec supports) can be input and stabilized for panning. Rigorous shaking such as at 15x zoom can still be too shaky for a reasonable result, and focused images work better than unfocused ones. Rotation and other changes are not yet supported, but as yet the speed is not bad: around 20 fps on an i7.

The speed is much better than before since now not the whole image is moved every time. Instead, the image is searched for the best corner points and then the corner points are tracked

<a href='http://www.youtube.com/watch?feature=player_embedded&v=aF9oJkn0328' target='_blank'><img src='http://img.youtube.com/vi/aF9oJkn0328/0.jpg' width='425' height=344 /></a>