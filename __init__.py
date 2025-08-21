import logging
from main import ReviewAnalysisApp

def main(req):
    logging.info("Azure Function triggered for Review Analysis.")
    # You can parse parameters from req if needed
    app = ReviewAnalysisApp()
    app.run()
    return "Review analysis completed and results exported."
