import pandas as pd
import numpy as np

def generate_dataset(num_records=1000):
    np.random.seed(42)
    
    # Generate random features
    cgpa = np.round(np.random.uniform(5.0, 10.0, num_records), 2)
    leetcode = np.random.randint(0, 1000, num_records)
    projects = np.random.randint(0, 10, num_records)
    internships = np.random.randint(0, 5, num_records)
    communication = np.random.randint(1, 11, num_records)
    
    # Calculate a composite score to determine placement probability
    # Weights for different factors
    score = (cgpa * 10) + (leetcode * 0.05) + (projects * 5) + (internships * 10) + (communication * 2)
    
    # Normalize score to 0-1 probability
    min_score, max_score = score.min(), score.max()
    prob = (score - min_score) / (max_score - min_score)
    
    # Determine placement (1 = Placed, 0 = Not Placed)
    placed = np.random.binomial(1, prob)
    
    # Calculate expected salary (in LPA) based on features
    base_salary = 3.0
    salary_multiplier = (cgpa * 0.5) + (leetcode * 0.002) + (projects * 0.3) + (internships * 0.5) + (communication * 0.2)
    salary = np.where(placed == 1, np.round(base_salary + salary_multiplier + np.random.normal(0, 1, num_records), 2), 0.0)
    # Ensure no negative salaries and reasonable min salary for placed
    salary = np.where((placed == 1) & (salary < 3.0), 3.0, salary)

    df = pd.DataFrame({
        'CGPA': cgpa,
        'LeetCode': leetcode,
        'Projects': projects,
        'Internships': internships,
        'Communication': communication,
        'Placed': placed,
        'Salary': salary
    })
    
    # Save to CSV
    df.to_csv('dataset/career_data.csv', index=False)
    print(f"Dataset with {num_records} records generated at 'dataset/career_data.csv'")

if __name__ == "__main__":
    generate_dataset()
