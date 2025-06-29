# %% Initialize PaddleOCR instance
from paddleocr import PaddleOCR
import time
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# %% Run OCR inference on a sample image 
# Time this
start_time = time.time()
for i in range(1, 4):
    result = ocr.predict(
        input=f"hw/hw_{i}.png")
   # Visualize the results and save the JSON results
    for res in result:
        res.print()
        res.save_to_img("output2")
        res.save_to_json("output2")

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")   
 
# %%
