# Delhi Bus Travel Time Prediction Using Machine Learning

## 1. Project Overview

The **Delhi Bus Travel Time Prediction Using Machine Learning** project focuses on analyzing historical bus movement data and predicting the time taken by a bus to travel between consecutive recorded nodes.

The project applies machine learning techniques to identify patterns in historical bus records and estimate travel-time intervals.

The main objective is to explore how machine learning can support travel-time estimation and contribute to intelligent public transportation systems.

The project covers data loading, preprocessing, exploratory data analysis, feature engineering, model training, performance evaluation, and result visualization.

## 2. Research Paper

The complete research paper explaining the project methodology, dataset, machine learning algorithms, experimental results, and findings is available below.

📄 **[Read Research Paper (PDF)](paper.pdf)**


## 3. Problem Statement

Public transportation systems generate large amounts of operational data. Analyzing this data can help identify travel patterns and estimate the time required for buses to move between recorded locations.

Travel time can vary depending on bus movement patterns, route direction, and the recorded node sequence.

The objective of this project is to develop a machine learning-based approach that uses historical bus records to estimate travel time between consecutive recorded nodes.

## 4. Project Objectives

- Analyze historical Delhi bus movement data.
- Process multiple Excel datasets.
- Perform data cleaning and preprocessing.
- Conduct exploratory data analysis.
- Extract useful features for machine learning.
- Train multiple regression models.
- Compare model performance using evaluation metrics.
- Visualize important findings and predictions.
- Identify the best-performing model among the tested approaches.

## 5. Dataset Description

The project uses bus-related historical data provided in multiple Excel workbooks.

The dataset is organized into three monthly folders:

- Month_1
- Month_2
- Month_3

Each monthly folder contains additional folders identified as `425` and `534`.

### Dataset Statistics

| Attribute | Value |
|---|---:|
| Total Excel files | 184 |
| Total records | 924,375 |
| Bus identifiers | 202 |
| Recorded node codes | 56 |
| Unreadable files | 0 |
| Missing values in core fields | 0 |

### Dataset Attributes

| Column | Description |
|---|---|
| Node | Recorded node code |
| Number | Bus identifier |
| Route | Recorded route direction |
| Time | Recorded time associated with the bus observation |



## 6. Technologies and Tools Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations |
| Scikit-learn | Machine learning |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| OpenPyXL | Reading Excel files |
| Joblib | Saving model artifacts |
| VS Code | Development environment |

## 7. Project Workflow

The project follows these major stages:

1. Load historical bus records from Excel files.
2. Combine records from monthly datasets.
3. Inspect and understand the dataset.
4. Perform data cleaning and preprocessing.
5. Identify consecutive node observations.
6. Calculate elapsed travel-time intervals.
7. Perform exploratory data analysis.
8. Prepare features and target variables.
9. Split the dataset into training and testing sets.
10. Train multiple regression models.
11. Evaluate and compare model performance.
12. Generate visualizations and save results.

### Workflow Diagram

```text
       Raw Excel Dataset
               |
               v
        Data Loading
               |
               v
      Data Preprocessing
               |
               v
     Feature Engineering
               |
               v
 Exploratory Data Analysis
               |
               v
       Train-Test Split
               |
               v
       Model Training
               |
               v
      Model Evaluation
               |
               v
     Model Comparison
               |
               v
     Results & Graphs
```

## 8. Data Preprocessing and Feature Engineering

Data preprocessing prepares the raw transportation records for machine learning.

The project performs the following operations:

- Loads multiple Excel workbooks.
- Combines records from monthly datasets.
- Checks missing values and data consistency.
- Processes bus identifiers and route directions.
- Identifies consecutive node records.
- Calculates elapsed time between consecutive observations.
- Filters invalid and unusually long intervals.
- Prepares the processed dataset for model training.

### Target Variable

The target variable represents the elapsed travel time between consecutive recorded node observations.

The project considers transitions where:

- The bus identifier remains the same.
- The recorded route direction remains the same.
- The next node code advances by exactly one.
- The calculated time interval is greater than zero.
- The time interval does not exceed 30 minutes.

These conditions help remove invalid transitions and unusually long intervals from the modeling dataset.

## 9. Machine Learning Algorithms

The project implements and compares five regression algorithms.

### 9.1 Linear Regression

Linear Regression models the relationship between input features and a continuous target variable. It provides a basic regression approach for estimating travel time.

### 9.2 Polynomial Regression

Polynomial Regression extends linear regression by introducing polynomial combinations of input features. The project uses degree 2 to capture nonlinear relationships.

### 9.3 K-Nearest Neighbors (KNN) Regression

KNN Regression predicts travel time using observations that are closest to the input sample. It relies on similarities between historical observations.

### 9.4 Decision Tree Regression

Decision Tree Regression uses decision rules to divide observations into smaller groups. It can capture nonlinear relationships between input features.

### 9.5 Multi-Layer Perceptron (MLP) Regression

MLP is a neural-network-based regression algorithm consisting of interconnected layers of neurons. It learns complex relationships from training data.

## 10. Baseline Models

The project also considers baseline approaches to evaluate whether machine learning models provide meaningful improvements.

- **Training Mean Baseline:** Predicts the average travel time from training data.
- **Segment Historical Mean:** Uses historical average travel time for a corresponding segment.
- **Persistence Baseline:** Uses a previous observed value as a prediction.

## 11. Model Evaluation Metrics

The models are evaluated using three regression metrics.

### Mean Absolute Error (MAE)

Measures the average absolute difference between actual and predicted values. Lower MAE indicates better prediction accuracy.

### Root Mean Squared Error (RMSE)

Measures prediction error while giving greater importance to larger errors. Lower RMSE indicates better performance.

### R-squared (R²)

Measures how much variation in the target variable is explained by the model. Higher R² generally indicates a better fit.

## 12. Model Performance and Results

The following table contains the previously saved model-comparison results.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Training Mean Baseline | 1.112 | 1.967 | -0.001 |
| Segment Historical Mean | 0.686 | 1.533 | 0.392 |
| Persistence Baseline | 1.422 | 2.513 | -0.634 |
| Linear Regression | 0.676 | 1.495 | 0.422 |
| Polynomial Regression | 0.644 | 1.469 | 0.442 |
| KNN Regression | 0.599 | 1.432 | 0.470 |
| Decision Tree Regression | 0.598 | 1.428 | 0.472 |
| MLP Regression | 0.596 | 1.426 | 0.474 |

### Initial Observations

- MLP Regression achieved the lowest MAE and RMSE among the previously saved results.
- MLP Regression also achieved the highest R² score.
- Decision Tree and KNN Regression demonstrated competitive performance.
- The results indicate that nonlinear models performed better than the basic linear model in this comparison.

*Note: These are previously saved comparison results. Verify the latest model-comparison output before treating them as the final results of a completed training run.*

## 13. Exploratory Data Analysis and Visualizations

Exploratory Data Analysis helps understand the structure and characteristics of the dataset.

The project generates visualizations to examine:

- Distribution of travel-time intervals.
- Bus movement patterns.
- Node-wise observations.
- Route-direction patterns.
- Relationships between input features.
- Model performance comparisons.
- Actual versus predicted values.
- Prediction errors and residual patterns.

Generated figures and tables are stored in the `outputs/` directory.

## 14. Project Directory Structure

```text
project/
│
├── .dist/
├── .venv/
│
├── data/
│   ├── Month_1/
│   ├── Month_2/
│   └── Month_3/
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── experiment_summary...
│   └── paper.docx
│
├── src/
│   ├── config.py
│   ├── load_data.py
│   ├── preprocess.py
│   ├── eda.py
│   ├── extra_analysis.py
│   ├── train_models.py
│   ├── paper_stats.py
│   ├── paper_content.py
│   ├── build_docx.py
│   ├── build_pdf.py
│   ├── plotstyle.py
│   ├── make_pipeline_figure.py
│   ├── make_result_figures.py
│   └── main.py
│
├── paper.pdf
├── README.md
├── requirements.txt
└── run_all.bat
```

## 15. Installation and Setup

Follow these steps to run the project locally.

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the Project Directory

```bash
cd project
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Add the Dataset

Place the original Excel files inside the `data/` directory while maintaining the monthly folder structure expected by the project configuration.

The raw dataset is not included in this GitHub repository.

## 16. How to Run the Project

### Option 1: Using the Batch File

On Windows, run:

```powershell
.\run_all.bat
```

### Option 2: Running Through Python

```bash
python src/main.py
```

The main script coordinates the project workflow according to the configured execution settings.

Generated analysis files, model comparisons, visualizations, and reports are saved in the `outputs/` directory.

**Important:** Check `src/config.py` and `requirements.txt` if dataset paths or dependencies need adjustment.

## 17. Limitations

The current project has the following limitations:

- The available dataset does not contain verified GPS coordinates.
- Actual bus-stop names and geographical locations are not established.
- Complete trip identifiers are not verified.
- Predictions represent intervals between consecutive recorded nodes, not complete journey arrival times.
- The dataset may not capture every factor affecting real-world bus travel time.
- Real-time traffic conditions and live GPS tracking are not integrated.

## 18. Future Scope

The project can be extended in several ways:

- Integrate official GTFS transportation data.
- Incorporate GPS coordinates and verified bus-stop information.
- Include real-time traffic conditions.
- Develop a real-time bus ETA prediction system.
- Explore advanced machine learning and deep learning algorithms.
- Build an interactive dashboard for displaying predictions.
- Integrate route visualization using mapping services.
- Evaluate model performance across different routes and time periods.

## 19. Conclusion

This project demonstrates how machine learning can be used to analyze historical bus movement records and estimate travel time between consecutive recorded nodes.

By implementing and comparing multiple regression algorithms, the project explores different approaches to transportation time prediction.

The workflow covers data preprocessing, exploratory analysis, feature engineering, model training, evaluation, and visualization.

The findings provide a foundation for developing more advanced intelligent transportation solutions using verified GPS, GTFS, and real-time traffic data.

## 20. Project Information

| Field | Details |
|---|---|
| Project Title | Delhi Bus Travel Time Prediction Using Machine Learning |
| Domain | Machine Learning and Data Science |
| Application Area | Transportation Analytics |
| Programming Language | Python |
| Development Environment | VS Code |
| Project Type | Academic Project |

---

