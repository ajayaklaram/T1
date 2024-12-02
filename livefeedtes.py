import cv2

# Camera credentials and IP details
username = "aajayk999%40gmail.com"  # Encoded '@' as '%40' in the username
password = "Ajay@123"
ip_address = "192.168.1.13"
port = "554"

# Possible RTSP URL formats to test
rtsp_urls = [
    f"rtsp://{username}:{password}@{ip_address}:{port}/stream",
    f"rtsp://{username}:{password}@{ip_address}:{port}/h264",
    f"rtsp://{username}:{password}@{ip_address}:{port}/live",
    f"rtsp://{username}:{password}@{ip_address}:{port}/stream1"
]

# Initialize a flag to track if a successful connection is made
connection_successful = False

# Test each RTSP URL
for rtsp_url in rtsp_urls:
    print(f"Trying RTSP URL: {rtsp_url}")
    try:
        # Force FFmpeg as backend
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Adjust buffer size to reduce timeouts

        if cap.isOpened():
            print("Video stream opened successfully with URL:", rtsp_url)
            connection_successful = True

            # Display the stream frame by frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to retrieve frame. There may be an issue with the network connection or camera stream.")
                    break

                # Display the resulting frame
                cv2.imshow('Live CCTV Stream', frame)

                # Press 'q' to quit the window
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release the video capture object and close display window
            cap.release()
            cv2.destroyAllWindows()
            break  # Exit the loop if a URL works

        else:
            print(f"Error: Could not open video stream with URL: {rtsp_url}")

    except cv2.error as e:
        print(f"OpenCV error occurred while trying URL: {rtsp_url}")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while trying URL: {rtsp_url}")
        print(f"Error details: {e}")

# Final message if none of the URLs worked
if not connection_successful:
    print("All RTSP URLs failed. Possible issues:")
    print("- Check if RTSP streaming is enabled on your camera.")
    print("- Verify that the IP address, port, username, and password are correct.")
    print("- Ensure your network or firewall is not blocking the RTSP port (usually 554).")
    print("- Try testing the RTSP URL in VLC Media Player to confirm connectivity.")

# Clean up and exit if no connection was successful
if cap and not cap.isOpened():
    cap.release()
cv2.destroyAllWindows()
