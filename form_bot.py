from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random
import time

from config import FORM_URL, MIN_DELAY, MAX_DELAY


# --------------------------------------------------
# Read feedback.txt
# --------------------------------------------------

def load_feedback(filename="feedback.txt"):
    records = []

    with open(filename, encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("---")

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        data = {}

        for line in block.splitlines():
            line = line.strip()

            if not line or "=" not in line:
                continue

            key, value = line.split("=", 1)

            data[key.strip()] = value.strip()

        records.append(data)

    return records


# --------------------------------------------------
# Random delay
# --------------------------------------------------

def wait_random():
    time.sleep(
        random.uniform(
            MIN_DELAY,
            MAX_DELAY
        )
    )


# --------------------------------------------------
# Validate input
# --------------------------------------------------

def validate_record(data):
    required = [
        "PROGRAMME",
        "DEPARTMENT",
        "SEMESTER",
        "COURSE_CODE",
        "INSTRUCTOR",
        "RATING",
        "COMMENT_INSTRUCTOR",
        "COMMENT_COURSE",
    ]

    missing = [
        key for key in required
        if key not in data
    ]

    if missing:
        raise ValueError(
            f"Missing fields: {', '.join(missing)}"
        )


# --------------------------------------------------
# Dropdown
# --------------------------------------------------

def choose_dropdown(page, label, value):

    print(f"Selecting {label}: {value}")

    dropdown = page.get_by_label(
        label,
        exact=True
    )

    dropdown.wait_for(
        state="visible"
    )

    dropdown.click()

    wait_random()

    option = page.get_by_role(
        "option",
        name=value,
        exact=True
    )

    option.wait_for(
        state="visible"
    )

    option.click()

    wait_random()


# --------------------------------------------------
# Email checkbox
# --------------------------------------------------

def select_email_checkbox(page):

    checkbox = page.get_by_role(
        "checkbox",
        name="Record b23cs037@nitm.ac.in as the email to be included with my response"
    )

    checkbox.wait_for(
        state="visible"
    )

    state = checkbox.get_attribute(
        "aria-checked"
    )

    print(
        f"Email checkbox before click: {state}"
    )

    if state != "true":

        checkbox.click()

        page.wait_for_function(
            """
            el => el.getAttribute("aria-checked") === "true"
            """,
            checkbox.element_handle()
        )

    print("Email checkbox selected.")

    wait_random()


# --------------------------------------------------
# Ratings
# --------------------------------------------------

def fill_all_ratings(page, rating=5):

    print(
        f"Selecting rating {rating}..."
    )

    radios = page.locator(
        f'div[role="radio"][aria-label="{rating}"]'
    )

    count = radios.count()

    print(
        f"Found {count} rating controls."
    )

    for i in range(count):

        radio = radios.nth(i)

        radio.scroll_into_view_if_needed()

        radio.click()

        time.sleep(0.15)

    wait_random()


# --------------------------------------------------
# Fill first page
# --------------------------------------------------

def fill_first_page(page, data):

    validate_record(data)

    print(
        f"\nCourse: {data['COURSE_CODE']}"
    )

    print(
        f"Instructor: {data['INSTRUCTOR']}"
    )

    # Email checkbox
    select_email_checkbox(page)

    # Programme
    choose_dropdown(
        page,
        "Programme",
        data["PROGRAMME"]
    )

    # Department
    choose_dropdown(
        page,
        "Department",
        data["DEPARTMENT"]
    )

    # Semester
    choose_dropdown(
        page,
        "Semester",
        data["SEMESTER"]
    )

    # Course code
    course_code = page.get_by_label(
        "Course Code",
        exact=True
    )

    course_code.fill(
        data["COURSE_CODE"]
    )

    wait_random()

    # Instructor
    choose_dropdown(
        page,
        "Course Instructor",
        data["INSTRUCTOR"]
    )

    # Next
    page.get_by_role(
        "button",
        name="Next",
        exact=True
    ).click()

    page.wait_for_load_state(
        "networkidle"
    )

    wait_random()


# --------------------------------------------------
# Fill second page
# --------------------------------------------------

def fill_second_page(page, data):

    print(
        "Filling feedback..."
    )

    # All ratings = 5
    fill_all_ratings(
        page,
        5
    )

    # Instructor comment
    instructor_comment = page.get_by_label(
        "Comments on Instructor",
        exact=True
    )

    instructor_comment.fill(
        data["COMMENT_INSTRUCTOR"]
    )

    # Course comment
    course_comment = page.get_by_label(
        "Comments on Course",
        exact=True
    )

    course_comment.fill(
        data["COMMENT_COURSE"]
    )

    wait_random()

    print(
        f"Finished filling {data['COURSE_CODE']}"
    )


# --------------------------------------------------
# Return to another response
# --------------------------------------------------

def start_another_response(page):

    print(
        "Looking for 'Submit another response'..."
    )

    link = page.get_by_text(
        "Submit another response",
        exact=True
    )

    link.wait_for(
        state="visible",
        timeout=10000
    )

    link.click()

    page.wait_for_load_state(
        "networkidle"
    )

    # Make sure the new form actually loaded
    page.get_by_role(
        "button",
        name="Next",
        exact=True
    ).wait_for(
        state="visible",
        timeout=10000
    )

    print(
        "New response form loaded."
    )

    wait_random()


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    records = load_feedback()

    if not records:
        print("No records found in feedback.txt")
        return

    print(
        f"Loaded {len(records)} records."
    )

    with sync_playwright() as p:

        # IMPORTANT:
        # Only ONE browser/context is created.
        context = p.chromium.launch_persistent_context(
            user_data_dir="./playwright-profile",
            headless=False,
        )

        try:

            page = (
                context.pages[0]
                if context.pages
                else context.new_page()
            )

            # Open form once
            page.goto(
                FORM_URL,
                wait_until="domcontentloaded"
            )

            page.wait_for_load_state(
                "networkidle"
            )

            for index, data in enumerate(records):

                print(
                    "\n"
                    + "=" * 50
                )

                print(
                    f"TEST RECORD {index + 1}/{len(records)}"
                )

                print(
                    "=" * 50
                )

                # --------------------------------
                # Page 1
                # --------------------------------

                fill_first_page(
                    page,
                    data
                )

                # --------------------------------
                # Page 2
                # --------------------------------

                fill_second_page(
                    page,
                    data
                )

                # --------------------------------
                # STOP BEFORE SUBMIT
                # --------------------------------

                print(
                    "\nForm is completely filled."
                )

                print(
                    "Stopping before Submit for testing."
                )

                page.get_by_role(
                    "button",
                    name="Submit",
                    exact=True
                ).click()
                
                page.wait_for_load_state("networkidle")
                
                if index < len(records) - 1:
                    start_another_response(page)

                break

        finally:

            context.close()


if __name__ == "__main__":
    main()