from data_processor import do_processing
from lstm_model import train_model


do_processing()
train_model("datasets/fugues.p")
