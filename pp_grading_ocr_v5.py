# %% Initialize PaddleOCR instance
from paddleocr import PaddleOCR
import time
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# # %% Run OCR inference on a sample image 
# # Time this
# start_time = time.time()
# result = ocr.predict(
#     input="homework_img/homework1.png")
# end_time = time.time()
# print(f"Time taken: {end_time - start_time} seconds")   
# # Visualize the results and save the JSON results
# for res in result:
#     res.print()
#     res.save_to_img("output")
#     res.save_to_json("output")
# %%
# %% Run OCR inference on a sample image 
# Time this
start_time = time.time()
result = ocr.predict(
    input="hw2/answer_key.png")
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")   
# Visualize the results and save the JSON results
for res in result:
    res.print()
    res.save_to_img("output2")
    res.save_to_json("output2")
# %%
# %% Run OCR inference on a sample image 
# Time this
start_time = time.time()
for i in range(1, 4):
    result = ocr.predict(
        input=f"hw2/hw{i}.png")
   # Visualize the results and save the JSON results
    for res in result:
        res.print()
        res.save_to_img("output2")
        res.save_to_json("output2")

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")   
 
# %%
