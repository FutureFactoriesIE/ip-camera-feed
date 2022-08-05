import cv2
cap = cv2.VideoCapture("rtsp://admin:123456@10.43.3.113/ch03/0")

while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
