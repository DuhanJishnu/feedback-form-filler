from playwright.sync_api import sync_playwright
import random
import time
from config import FORM_URL, HEADLESS, MIN_DELAY, MAX_DELAY, EMAIL


# -------------------------------
# Read feedback file
# -------------------------------

def load_feedback(filename="feedback.txt"):
    students = []

    with open(filename, encoding="utf-8") as f:
        blocks = f.read().split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        data = {}
        for line in block.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()

        students.append(data)

    return students


def wait():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


# -------------------------------
# Dropdown Helper
# -------------------------------

def choose_dropdown(page, label, value):
    page.get_by_label(label).click()
    wait()
    page.get_by_role("option", name=value, exact=True).click()

def select_email_checkbox(page):
    checkbox = page.get_by_role(
        "checkbox",
        name=f"Record {EMAIL} as the email to be included with my response"
    )

    checkbox.wait_for(state="visible")

    print(
        "Initial checkbox state:",
        checkbox.get_attribute("aria-checked")
    )

    if checkbox.get_attribute("aria-checked") != "true":
        checkbox.click()

        page.wait_for_function(
            """el => el.getAttribute("aria-checked") === "true" """,
            arg=checkbox.element_handle()
        )

    print(
        "Final checkbox state:",
        checkbox.get_attribute("aria-checked")
    )

# -------------------------------
# Rating Helper
# -------------------------------

def fill_all_ratings(page, rating_value):
    """
    Google Form contains 19 linear scale questions.
    Clicks value 1-5 for every question.
    """

    radios = page.locator(f'div[role="radio"][aria-label="{rating_value}"]')

    count = radios.count()

    for i in range(count):
        radios.nth(i).click()
        time.sleep(0.15)


# -------------------------------
# Fill One Form
# -------------------------------

def submit_test_feedback(page, data):
    """
    Fill one test response and submit it.
    Intended for a form you own or are authorized to test.
    """

    select_email_checkbox(page)
    # Fill the first page
    choose_dropdown(page, "Programme", data["PROGRAMME"])
    choose_dropdown(page, "Department", data["DEPARTMENT"])
    choose_dropdown(page, "Semester", data["SEMESTER"])

    page.get_by_label("Course Code").fill(data["COURSE_CODE"])

    choose_dropdown(
        page,
        "Course Instructor",
        data["INSTRUCTOR"]
    )

    page.get_by_role("button", name="Next").click()

    page.wait_for_load_state("networkidle")

    # Select rating 5 for the rating questions
    fill_all_ratings(page, 5)

    # Comments
    page.get_by_label("Comments on Instructor").fill(
        data["COMMENT_INSTRUCTOR"]
    )

    page.get_by_label("Comments on Course").fill(
        data["COMMENT_COURSE"]
    )

    # Submit
    page.get_by_role("button", name="Submit").click()

    page.wait_for_load_state("networkidle")

    print(f"Test response submitted: {data['COURSE_CODE']}")

def start_another_test_response(page):
    """
    Return from the confirmation page to the form.
    """

    another_response = page.get_by_text(
        "Submit another response",
        exact=True
    )

    another_response.wait_for(timeout=10000)
    another_response.click()

    page.wait_for_load_state("networkidle")

    print("Ready for next test response.")

# -------------------------------
# Main
# -------------------------------

def main():

    students = load_feedback()  

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="./playwright-profile",
            headless=HEADLESS,
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Open the form only once
        page.goto(FORM_URL)

        page.wait_for_load_state("networkidle")

        for index, student in enumerate(students):

            print(
                f"\nProcessing test response "
                f"{index + 1}/{len(students)}"
            )

            submit_test_feedback(page, student)

            # Don't try to start another response
            # after the final test record.
            if index < len(students) - 1:
                start_another_test_response(page)

        context.close()


if __name__ == "__main__":
    main()