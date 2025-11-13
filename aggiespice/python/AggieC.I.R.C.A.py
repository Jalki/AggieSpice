import numpy as np # linear algebra library
import pandas as pd # data processing library
import seaborn as sns # data visualization library //KEY FOR FUN STUFF
from sklearn.model_selection import train_test_split # train-test split function
from sklearn.preprocessing import StandardScaler # feature scaling function
from sklearn.ensemble import RandomForestClassifier # random forest classifier
from sklearn.metrics import classification_report, confusion_matrix     # model evaluation functions
from sklearn import metrics # additional metrics functions
from sklearn.svm import SVC # support vector machine classifier
from xgboost import XGBClassifier # extreme gradient boosting classifier
from sklearn.linear_model import LogisticRegression # logistic regression classifier
import matplotlib.pyplot as plt # plotting library, this will
import os # operating system library
import Dataset as dset # custom dataset module
#import pytorch as torch # deep learning library



#---AggieC.I.R.C.A (Circuit Intelligence for Reasoning and Analysis) is the AggieSpice Customizable Intelligent Robotic Command Assistant---#
#---Developed for ECEN 377 at North Carolina Argicultural and Technical State University---#
#---Main Developer: Jaleen Bowens-Kelly---#

class AggieCIRCA:
    def __init__(self, name="AggieCIRCA"):
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"{self.name} initialized and ready for tasks.")

    # Data Preprocessing

    #Machine Learning Model Training; Used for smaller datasets (Like voltage drops, etc) that does not require deep learning. DOES NOT HANDLE IMAGES! Thats for Deep Learning Model Training!
    
    def train_model(self, data, target_column):
        

    #Deep Learning Model Training; Used for larger datasets (Like images, video, etc) that require deep learning. Users can give