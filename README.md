# CITS5505 Group Project - FitTracker

## Project Description
FitTracker is a fitness analytics web application that allows users to upload their exercise, diet, and sleep data. The application provides visual insights and summaries through interactive charts and allows users to selectively share their data with others.

## Team Members

| UWA ID   | Name             | GitHub Username  |
|----------|------------------|------------------|
| 24269773 | Xu Li            | XuLi111111       |
| 24495786 | Fei Han          | FeiHan69         |
| 24389999 | Arthur Zhang     | arthur-zhang-THU |
| 23981757 | Harshit Gadhiya  | harshit-3        |

## How to Run

1. Clone the repository and navigate to the project directory:

    ```bash
    git clone https://github.com/harshit-3/CITS_5505_Group_25.git
    cd CITS_5505_Group_25
    ```

2. (Optional) Create and activate a virtual environment:

    ```bash
    python -m venv myenv
    source myenv/bin/activate       # For macOS/Linux
    myenv\Scripts\activate          # For Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    flask db upgrade
    flask run
    ```

5. Open your browser and go to:  
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to Run Tests

### Unit Tests

Run all tests using:

```bash
pytest tests
```


