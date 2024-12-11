import os
import re
from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime


def text_to_image(text_body):
    text_body, hashtags = format_text(text_body)
    image_path = generate_image(text_body, hashtags)
    return {
        "text": text_body,
        "hashtags": hashtags,
        "image_path": image_path,
        # "media_id": media,
    }


def format_text(text_body):
    hashs = re.findall(r"#\w+", text_body)

    hashtags = []
    for word in text_body.split()[::-1]:
        if word in hashs:
            hashtags.append(word)
        else:
            break

    for hash in hashtags:
        text_body = text_body.replace(hash, "")

    text_body = text_body.strip()
    hashtags = hashtags[::-1]
    hashtags = " ".join(hashtags)
    return text_body, hashtags


def generate_image(tweet_body, hashtags):

    img = Image.new("RGBA", (1200, 1200), color=(28, 28, 30))

    # background_image_path = "background.png"
    # background_image = Image.open(background_image_path)
    # background_image = background_image.convert('RGBA')
    # background_image = background_image.resize((1200, 1200))
    # img = Image.alpha_composite(img, background_image)

    draw = ImageDraw.Draw(img)

    font_path = "fonts/Chirp.ttf"
    username_font_path = "fonts/comics_grass.ttf"

    username_font_size = 30
    description_font_size = 55
    hashtags_font_size = 37

    username_font = ImageFont.truetype(username_font_path, size=username_font_size)
    description_font = ImageFont.truetype(font_path, size=description_font_size)
    hashtags_font = ImageFont.truetype(font_path, size=hashtags_font_size)

    username_text = os.getenv("IMAGE_WATERMARK")
    description_text = tweet_body
    hashtags_text = hashtags

    center_x = img.width / 2
    start_x = 150
    center_y = img.height / 2 - 100

    description_text = description_text.replace("\n", "\n‎")
    description_text_elements = description_text.split("\n")
    description_text_wrapped = []
    for description_text_element in description_text_elements:
        description_text_wrap = textwrap.wrap(
            description_text_element,
            width=30,
            replace_whitespace=False,
            expand_tabs=False,
        )
        description_text_wrapped.extend(description_text_wrap)

    description_positions = []
    line_size_0 = draw.textsize(description_text_wrapped[0], font=description_font)
    for index, line in enumerate(description_text_wrapped):
        line_size = draw.textsize(line, font=description_font)
        line_position = (
            start_x,
            center_y - ((len(description_text_wrapped) / 2) - index) * line_size_0[1],
        )
        description_positions.append(line_position)

    description_color = (229, 222, 211)
    for i, position in enumerate(description_positions):
        draw.text(
            position,
            description_text_wrapped[i],
            fill=description_color,
            font=description_font,
        )

    description_start = description_positions[0]
    description_end = description_positions[len(description_positions) - 1]

    hashtags_size = draw.textsize(hashtags_text, font=hashtags_font)
    hashtags_position = start_x, description_end[1] + 60 + hashtags_size[1]

    hashtags_color = (53, 76, 124)
    draw.text(hashtags_position, hashtags_text, fill=hashtags_color, font=hashtags_font)

    username_size = draw.textsize(username_text, font=username_font)
    # username_position = start_x, hashtags_position[1] + 50 + username_size[1]
    username_position = 900, 1130
    username_color = (193, 85, 82)
    draw.text(username_position, username_text, fill=username_color, font=username_font)

    output_size = (1200, 1200)
    img = img.resize(output_size)
    utc_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # ist_now = utc_now.astimezone(ist_timezone)
    image_path = f"data/{utc_now}.png"
    img.save(image_path, quality=100)

    return image_path
