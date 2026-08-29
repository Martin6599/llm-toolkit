from text_utils import read_text_auto, wash_text
raw = read_text_auto("test_data/test_gbk.txt")   # 编码回退生效
print(wash_text(raw))