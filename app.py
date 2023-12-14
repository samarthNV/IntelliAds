import os
import cv2
import textwrap
import pywhatkit
import random
import smtplib
from dotenv import load_dotenv
from bardapi import BardCookies
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

load_dotenv()

cookie_dict = {
    "__Secure-1PSID": os.getenv("Secure_1PSID"),
    "__Secure-1PSIDTS": os.getenv("Secure_1PSIDTS"),
}

bard = BardCookies(cookie_dict=cookie_dict)

# data = bard.get_answer("Generate a very short, personalised and creative advertisement for a coding course of DATA structures AND ALGORITHMS  by coding ninjas. Customer Name - Siddhesh, Customer Interest - Cricket. Generate four lines and escape the begining part where you brief about the prompt.")

# content = data['content']
# content_without_asterisks = content.replace('*', '')

# text = content_without_asterisks
# heading = "Coding Course"

def create_prompt_from_description(customer_name, customer_interests, product_name, delivery_platform="WhatsApp"):
    prompt = "Generate a creative personalized according to customer's interests' short text-based advertisement to " \
             "be delivered on '" + delivery_platform + "' including emojis for the product - '" + product_name +  \
            "'. The advertisement is to be delivered to the customer named '" + customer_name + \
             "' whose interests are as follows - '" + customer_interests + "'. No need of Hashtags. No need of product " \
            "link. Start with response directly. "

    return prompt

heading = "Coding Course"
query = create_prompt_from_description("Samarth", "loves to play cricket", heading)
data = bard.get_answer(query)
content = data['content']
content_without_asterisks = content.replace('*', '')

text = content_without_asterisks


def put_text(img, text, x_value, y_value):
    font = cv2.FONT_HERSHEY_DUPLEX
    wrapped_text = textwrap.wrap(text, width=28)
    x, y = 200, 40
    font_size = 1.25
    font_thickness = 2

    for i, line in enumerate(wrapped_text):
        textsize = cv2.getTextSize(line, font, font_size, font_thickness)[0]

        gap = textsize[1] + 30
        y = y_value + i * gap
        #y = int((img.shape[0] + textsize[1]) / 2) + i * gap
        x = int((img.shape[1] - textsize[0]) / 2)
        cv2.putText(img, line, (x_value, y), font,
                    font_size,
                    (0,0,0),
                    font_thickness,
                    lineType = cv2.LINE_AA)

def put_heading(img, text, x_value, y_value):
    font = cv2.FONT_HERSHEY_DUPLEX
    wrapped_text = textwrap.wrap(text, width=28)
    x, y = 200, 40
    font_size = 2.5
    font_thickness = 3

    for i, line in enumerate(wrapped_text):
        textsize = cv2.getTextSize(line, font, font_size, font_thickness)[0]

        gap = textsize[1] + 30
        y = y_value + i * gap
        #y = int((img.shape[0] + textsize[1]) / 2) + i * gap
        x = int((img.shape[1] - textsize[0]) / 2)
        cv2.putText(img, line, (x_value, y), font,
                    font_size,
                    (0,0,0),
                    font_thickness,
                    lineType = cv2.LINE_AA)
        
def overlay_images(background_image_path, overlay_image_path, x_position, y_position):
    # Read the images
    background_image = cv2.imread(background_image_path)
    overlay_image = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)

    # Get the dimensions of the overlay image
    overlay_height, overlay_width = overlay_image.shape[:2]

    # Resize the overlay image to 1/8 of its original size
    resized_overlay = cv2.resize(overlay_image, (overlay_width // 1, overlay_height // 1))

    # Get the new dimensions of the resized overlay
    resized_height, resized_width = resized_overlay.shape[:2]

    # Compute the region of interest (ROI) for the overlay image
    roi = background_image[y_position:y_position + resized_height, x_position:x_position + resized_width]

    # If the overlay image has an alpha channel
    if resized_overlay.shape[-1] == 4:
        # Extract the alpha channel from the resized overlay
        alpha_channel = resized_overlay[:, :, 3] / 255.0  # Normalize to [0, 1]

        # Create a mask using the normalized alpha channel
        mask = cv2.merge((alpha_channel, alpha_channel, alpha_channel))

        # Use the mask to blend the images
        blended_roi = cv2.addWeighted(roi, 1 - alpha_channel, resized_overlay[:, :, :3], alpha_channel, 0)

        # Update the background image with the blended ROI
        background_image[y_position:y_position + resized_height, x_position:x_position + resized_width] = blended_roi

    else:
        # If there is no alpha channel, directly overlay the images
        background_image[y_position:y_position + resized_height, x_position:x_position + resized_width] = resized_overlay

    return background_image

# random_number = random.uniform(1, 5)
# n = str(random_number)
# num = "image" + n + ".jpg"
img = cv2.imread("image1.jpg")
put_text(img, text, 400, 450)
cv2.imwrite("output.jpg", img)
img2 = cv2.imread("output.jpg")
put_heading(img2, heading, 250, 250)
cv2.imwrite("output2.jpg", img2)
img3 = overlay_images('output2.jpg', 'coding.jpg', 40, 650)
cv2.imwrite("final.jpg", img3)

ad = "final.jpg"
 

sender_email = 'samarth.bura21@vit.edu'
sender_password = os.getenv("Email_password")

# Set the recipient email address
recipient_email = 'samarthvbura@gmail.com'

# Create the MIME object
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = recipient_email
message['Subject'] = heading

# Attach the email body
body = 'This is the body of the email.'
message.attach(MIMEText(body, 'plain'))

# Attach the image (change 'path/to/your/image.jpg' to the actual path of your image file)
image_path = 'final.jpg'
with open(image_path, 'rb') as image_file:
    image_data = image_file.read()
    image = MIMEImage(image_data, name='final.jpg')
    message.attach(image)

# Establish a connection to the SMTP server (in this case, Gmail's SMTP server)
with smtplib.SMTP('smtp.gmail.com', 587) as server:
    # Start the TLS connection
    server.starttls()

    # Log in to the email account
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, recipient_email, message.as_string())

print('Email sent successfully!')


pywhatkit.sendwhats_image("+91 8080063254", ad, "Do Register !!!", 20)
print('Whatsapp message sent successfully!')
