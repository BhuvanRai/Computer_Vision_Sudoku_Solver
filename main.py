import cv2
import numpy as np
import imutils
from imutils.perspective import four_point_transform
import tensorflow as tf
from sudoku_solver import Sudoku
import copy

model = tf.keras.models.load_model(
    r"F:\Coding\project\Computer_vision_sudoku_solver\mnist_digit_model3_finetuned_on_1_and_5.keras"
)

sudo_collection = [[[0]*30 for _ in range(9)] for _ in range(9)]

collection_idx = 0

initial_frames = 5

solved_overlay = None

final_sudo = [[0]*9 for _ in range(9)]

sudoku_clr = None

cap=cv2.VideoCapture(1)

while cap.isOpened():
    ret,frame = cap.read()

    if not ret:
        continue
    
    frame = cv2.resize(frame,(600,600))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (5,5), 0) 
    adTh = cv2.adaptiveThreshold( blur, 255, 1, 1, 11, 5 )
    img_lines=adTh.copy()


    lines = cv2.HoughLinesP( adTh, 1, 
        np.pi/180, 100, 
        minLineLength=100, 
        maxLineGap=10 
    )
    

    try:
        for x1, y1, x2, y2 in lines[:,0,:]: 
            cv2.line(img_lines,(x1,y1), (x2,y2), (255,255,255),2)
    except:
        pass

    cnts = cv2.findContours(img_lines.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

    cn_img = frame.copy()

    for (i,c) in enumerate(cnts):
        peri = cv2.arcLength(c, True)    
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        if len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            
            if ar >= 1.25 or ar <= 0.75:
                continue
            
            if w*h < 200000:
                continue

            mainCnt = approx
            full_coords = mainCnt.reshape(4, 2)
            cv2.drawContours(
                cn_img,
                [mainCnt],
                -1,
                (0,0,0),
                -1
            )
            sudoku = four_point_transform(img_lines, mainCnt.reshape(4, 2))

            sudoku_clr = four_point_transform(frame, mainCnt.reshape(4, 2))


            sud_c = sudoku.copy()

            if sudoku is None:
                continue

            if sudoku.shape[0] < 50 or sudoku.shape[1] < 50:
                continue

            horizontal = np.copy(sud_c)
            vertical = np.copy(sud_c)
            
            cols = horizontal.shape[1]
            horizontal_size = cols // 10
            horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
            horizontal = cv2.erode(horizontal, horizontalStructure)
            horizontal = cv2.dilate(horizontal, horizontalStructure)
            
            rows = vertical.shape[0]
            verticalsize = rows // 10
            verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
            vertical = cv2.erode(vertical, verticalStructure)
            vertical = cv2.dilate(vertical, verticalStructure)
            
            grid = cv2.bitwise_or(horizontal, vertical)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
            grid = cv2.dilate(grid, kernel)
            
            grid = cv2.bitwise_and(grid, sudoku)

            num = cv2.bitwise_xor(sud_c, grid)

            if (full_coords[0][0])**2 + (full_coords[0][1])**2 < \
            (full_coords[1][0])**2 + (full_coords[1][1])**2:

                sud_coords = np.array([
                    [0, 0],
                    [0, num.shape[0]],
                    [num.shape[1], num.shape[0]],
                    [num.shape[1], 0]
                ], dtype=np.float32)

            else:

                sud_coords = np.array([
                    [num.shape[1], 0],
                    [0, 0],
                    [0, num.shape[0]],
                    [num.shape[1], num.shape[0]]
                ], dtype=np.float32)

            num_r_size = num.shape[0]
            num_c_size = num.shape[1]

            window_r = num_r_size//9 
            window_c = num_c_size//9 

            smallest_area = (window_c*window_r)//10

            error_r = window_r // 9 
            error_c = window_c // 9

            digit_imgs = []
            digit_pos = []

            for r in range(9):
                for c in range(9):

                    crop = num[r*window_r+error_r:r*window_r-error_r+window_r, window_c*c+error_c:c*window_c-error_c+window_c]                    
                    
                    proposals = cv2.findContours(
                        crop,
                        cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE
                    )
                    proposals = imutils.grab_contours(proposals)
                    
                    if len(proposals) > 0:
                        digit = sorted(proposals, key = cv2.contourArea, reverse = True)[0]
                        perimeter = cv2.arcLength(digit, True)
                        approx_shape = cv2.approxPolyDP(digit, 0.02 * perimeter, True)
                        bound_rect = cv2.boundingRect(approx_shape)
                        
                        rect_area = bound_rect[2] * bound_rect[3]
                    
                        if rect_area < smallest_area:
                            continue
                        
                        
                        (x,y,w,h) = bound_rect

                        cv2.rectangle(sudoku_clr, (c*window_c+x+error_c, r*window_r+y+error_r),
                                      (c*window_c+x+w+error_c, r*window_r+y+h+error_r),
                                      (0, 255, 0), 1)

                        try:
                            prop = crop[y:y+h, x:x+w]

                            side = max(w, h)+6
                            square = np.zeros((side, side), dtype=np.uint8)

                            yoff = (side - h) // 2
                            xoff = (side - w) // 2

                            square[yoff:yoff+h, xoff:xoff+w] = prop

                            prop = cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA)

                            if np.mean(prop) > 127:
                                prop = 255 - prop

                            prop = prop.astype(np.float32) / 255.0

                            digit_imgs.append(prop)
                            digit_pos.append((r, c))

                        except Exception as e:
                            print(e)

            sudo = [[0]*9 for _ in range(9)]
            if len(digit_imgs)>15:

                batch = np.array(digit_imgs)

                batch = np.expand_dims(batch, axis=-1)

                preds = model.predict(batch, verbose=0)

                preds = np.argmax(preds, axis=1)

                for pred, (r, c) in zip(preds, digit_pos):
                    sudo[r][c] = int(pred)
            
            
            if(collection_idx<15):
                for i in range(9):
                    for j in range(9):
                        sudo_collection[i][j][collection_idx] = sudo[i][j]
            if(collection_idx == 15):
                for i in range(9):
                    for j in range(9):
                        score = [0.0]*10
                        for k in range(15):
                                score[sudo_collection[i][j][k]] += 1.0
                        if(score[1]>2):
                            final_sudo[i][j]=1
                        elif(score[4]>2):
                            final_sudo[i][j]=4
                        elif(score[5]>2):
                            final_sudo[i][j]=5
                        else:
                            final_sudo[i][j] = int(np.array(score).argmax())
                print(final_sudo)
                temp = temp = copy.deepcopy(final_sudo)
                sudo = Sudoku(final_sudo)
                if sudo.solved:
                    
                    solved_board = sudo.board
                    
                    for r in range(9):
                        for c in range(9):

                            if temp[r][c] != 0:
                                continue
                            
                            x = c * window_c + window_c // 3
                            y = r * window_r + (2 * window_r) // 3

                            cv2.putText(
                                sudoku_clr,
                                str(solved_board[r][c]),
                                (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 0),
                                2,
                                cv2.LINE_AA
                            )

                    height, width = frame.shape[:2]

                    H, _ = cv2.findHomography(
                        sud_coords,
                        full_coords.astype(np.float32)
                    )

                    im_out = cv2.warpPerspective(
                        sudoku_clr,
                        H,
                        (width, height)
                    )

                    final_im = cv2.add(cn_img, im_out)
                    solved_overlay = final_im
                        

                sudo_collection = [[[0]*30 for _ in range(9)] for _ in range(9)]
                final_sudo = [[0]*9 for _ in range(9)]

                collection_idx = -1
            collection_idx+=1
        break
    if(sudoku_clr is not None):
        cv2.imshow("sudoku",sudoku_clr)
    
    if (solved_overlay is not None):
        cv2.imshow("final_img",solved_overlay)
    cv2.imshow("frame",frame)
    cv2.waitKey(10)

cv2.destroyAllWindows()
