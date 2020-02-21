#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import numpy as np
import pandas as pd
import shap


# Training a Model
# ================
#
# We begin by loading in a standard data set (Iris) and training a Boolean classifier.
#
# For each row we will be asking the question, Is this a versicolor iris?
#
# We will be using the Xgboost gbtree classifier for this experiment.

# In[2]:


# Load data

data = load_iris()
target = np.where(data["target"] == 1, data["target"], 0)
data_train, data_test, target_train, target_test = train_test_split(data["data"], target, random_state=1000)


# In[3]:


# Train classifier and score testing data.

model = XGBClassifier()
model.fit(data_train, target_train)
results = model.predict_proba(data_test)[:,1]
results


# Margins
# ------
#
# Each score from XGBoost is actually a linear score (-inf, inf) that is normalized to a probability when requested.
#
# Essentially each tree in the forest generates a number (margin) which is summed across the whole forest to create the final output of the model.
#
# We can access these margins through XGBoost directly

# In[4]:


margin = model.predict(data_test, output_margin=True)
margin


# In[5]:


# Summarize prediction Results

dfResults = pd.DataFrame(data_test)
dfResults.columns = data["feature_names"]
dfResults["versicolor_prob"] = results
dfResults["versicolor_margin"] = margin
dfResults


# Now let's try to explain some of these values.

# SHAP - Shapley Value
# ====
#
# SHAP attempts to determine which features were responsible for which portion of the margin.
#
# SHAP is originally a concept from cooperative game theory. It attempts to divide value amount a group of cooperative workers according to the following axioms.
#
# - All value is assigned to at least one actor.
# - Two actors who contribute equally receive equal value.
# - Actors who provide no value receive no value.
# - And a few other math technicalities.
#
# In short, SHAP divides up the margin and tries to determine how much of it each feature is responsible for.

# In[6]:


# Generate shap data

explainer = shap.TreeExplainer(model, data=data_train)
shap_values = explainer.shap_values(data_test)


# In[7]:


explainer.expected_value


# Firstly, it's important to understand that the SHAP library always makes reference to the model's expected value.
#
# The expected value is roughly equal to the average output of the model given random data.
#
# Since there were a lot more examples in the training data that are not versicolor it makes sense that the expected value is negative. Given a random example the output is less
# likely to be versicolor.
#
# Individual SHAP values always sum up to a predictions "shift", the difference between the margin and the model's expected value.

# In[8]:


# Combine everything into a formatted dataframe.

dfShaps = pd.DataFrame(shap_values)
dfShaps.columns = [i + "_shap" for i in data["feature_names"]]
dfJoined = pd.merge(dfResults, dfShaps, left_index=True, right_index=True)
dfJoined["shift"] = dfJoined["versicolor_margin"].apply(lambda x: x - explainer.expected_value)
dfJoined["target"] = target_test
dfJoined = dfJoined[["sepal length (cm)", "sepal length (cm)_shap", "sepal width (cm)", "sepal width (cm)_shap", "petal length (cm)", "petal length (cm)_shap", "petal width (cm)", "petal width (cm)_shap", "versicolor_margin", "shift", "versicolor_prob", "target"]]
dfJoined


# Now let's take a look at row 9 and attempt to use SHAP to explain why it is not a versicolor.

# In[9]:


#print(dfJoined.iloc[9:10])


# In[10]:


shap.initjs()
shap.force_plot(explainer.expected_value, shap_values[9], data["feature_names"])
dfJoined.to_csv("shap.csv", sep='\t', index = False)
