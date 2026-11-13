from drafter import *
from dataclasses import dataclass, field
from datetime import date, time, timedelta


# Stores information about each recommendation
@dataclass
class RecommendationData:
    title: str
    category: str
    price_estimate: str
    description: str
    location: str
    tip: str


# Stores one event the user saved, with the day and time they planned it for
@dataclass
class SavedEvent:
    title: str
    planner: str
    category: str
    price_estimate: str
    location: str
    day: str
    time: str


# Stores information throughout the website
@dataclass
class State:
    current_route: str
    previous_route: str
    restore_phrase: str
    phrase_attempt: str
    wikipedia_feedback: str

    honeymoon_budget: str
    honeymoon_dest: str

    party_type: str
    party_honor_guest: str

    date_activity: str
    date_timestamp: str

    recommendations: list[RecommendationData] = field(default_factory=list)
    error_message: str = ""
    date_day: str = ""
    date_time: str = "7:00 PM"

    saved_events: list[SavedEvent] = field(default_factory=list)
    save_day: str = ""
    save_time: str = "7:00 PM"
    notice: str = ""


# ---------- LOOK AND FEEL ----------
ROSE = "#b5446e"
DEEP_ROSE = "#8e2f56"

# Builds a Page with the shared theme applied
def themed_page(state: State, content: list) -> Page:
    wrapper = Div(*content)
    wrapper = change_background_color(wrapper, "#fff5f7")
    wrapper = change_color(wrapper, "#4a2b37")
    wrapper = change_text_font(wrapper, "Georgia, serif")
    wrapper = change_padding(wrapper, "16px 24px")
    return Page(state, [wrapper])


# Rose-colored button (styled with Drafter's style_ keyword arguments)
def rose_button(text: str, url, arguments=None):
    if arguments is None:
        return Button(text, url,
                      style_background_color=ROSE, style_color="white")
    return Button(text, url, arguments,
                  style_background_color=ROSE, style_color="white")


# Centered title block with a subtitle and a divider
def page_title(title: str, subtitle: str = ""):
    return change_text_align(
        Div(
            change_color(Header(title, 1), DEEP_ROSE),
            italic(subtitle),
            HorizontalRule()
        ),
        "center"
    )


# Small colored section label
def section_label(text: str):
    return change_color(bold(text), DEEP_ROSE)


# White rounded-looking card with a soft border
def card(*items):
    box = Div(*items)
    box = change_background_color(box, "#ffffff")
    box = change_padding(box, "14px 18px")
    box = change_margin(box, "12px 0")
    box = change_border(box, "solid 1px #e8c4d1")
    return box


# Soft highlighted banner for important info
def banner(text: str):
    box = Div(bold(text))
    box = change_background_color(box, "#fde4ec")
    box = change_padding(box, "10px 16px")
    box = change_margin(box, "10px 0")
    box = change_text_align(box, "center")
    return box


# Red-ish warning text
def warning_text(text: str):
    return change_color(bold(text), "#c0392b")


# Helper to return the user to whichever page they were just on
def return_to_current_page(state: State) -> Page:
    if state.current_route == "honeymoon":
        return honeymoon(state)
    elif state.current_route == "honeymoon_res":
        return recommendation_page(state, "Honeymoon Recommendations")
    elif state.current_route == "party":
        return party(state)
    elif state.current_route == "party_res":
        return recommendation_page(state, "Party Recommendations")
    elif state.current_route == "datenight":
        return datenight(state)
    elif state.current_route == "datenight_res":
        return recommendation_page(state, "Date Night Recommendations")
    else:
        return home(state)


# HOME PAGE
@route
def index(state: State) -> Page:
    return home(state)


@route
def home(state: State) -> Page:
    state.current_route = "home"
    warning = state.error_message
    state.error_message = ""

    notice = state.notice
    state.notice = ""

    content = [
        page_title("SECRET EVENT PLANNER \u2665",
        "Welcome! What would you like to plan?"),
        card(
            section_label("Choose a planner"),
        "\n",
            rose_button("Plan a Honeymoon", "home_action",
                   [Argument("action", "honeymoon")]),
            rose_button("Plan a Surprise Party", "home_action",
                   [Argument("action", "party")]),
            rose_button("Plan a Date Night", "home_action",
                   [Argument("action", "datenight")])
        ),
        saved_events_section(state),
        card(
            section_label("Secret phrase"),
        "\n",
        "Create a secret phrase to return to your previous page:",
        "\n",
            TextBox("new_restore_phrase", state.restore_phrase),
            rose_button("Save Phrase", "home_action",
                   [Argument("action", "save")]),
        "\n",
            rose_button("Discreet Exit", "home_action",
                   [Argument("action", "panic")])
        )
    ]

    if notice != "":
        content.insert(1, banner(notice))

    if warning != "":
        content.append(banner(warning))

    return themed_page(state, content)


# Builds the "Saved Events" section shown on the home page
def saved_events_section(state: State):
    items = [section_label("Saved events"), "\n"]

    if len(state.saved_events) == 0:
        items.append(italic("Nothing saved yet. Open any planner, get "
                            "recommendations, and press Save on the ones "
                            "you like."))
    else:
        items.append(small_font("You have " + str(len(state.saved_events))
                                + " saved."))
        for i, event in enumerate(state.saved_events):
            items.append(
                card(
                    change_color(Header(event.title, 4), DEEP_ROSE),
                    Span(bold("When: "), event.day + " at " + event.time),
                    "\n",
                    Span(bold("Planner: "), event.planner),
                    "\n",
                    Span(bold("Category: "), event.category),
                    "\n",
                    Span(bold("Estimated Cost: "), event.price_estimate),
                    "\n",
                    Span(bold("Location: "), event.location),
                    "\n",
                    rose_button("Remove", "remove_saved_event",
                                [Argument("index", str(i))])
                )
            )

    return card(*items)


@route
def remove_saved_event(state: State, index: str) -> Page:
    i = int(index)
    if 0 <= i < len(state.saved_events):
        removed = state.saved_events.pop(i)
        state.notice = "Removed \"" + removed.title + "\" from saved events."
    return home(state)


@route
def save_event(state: State, index: str, save_day: str,
               save_time: str) -> Page:
    i = int(index)
    state.save_day = save_day
    state.save_time = save_time

    if 0 <= i < len(state.recommendations):
        rec = state.recommendations[i]

        if state.current_route == "honeymoon_res":
            planner = "Honeymoon"
        elif state.current_route == "party_res":
            planner = "Surprise Party"
        else:
            planner = "Date Night"

        already_saved = False
        for event in state.saved_events:
            if (event.title == rec.title and event.day == save_day
                    and event.time == save_time):
                already_saved = True

        if already_saved:
            state.notice = ("\"" + rec.title + "\" is already saved for "
                            + save_day + " at " + save_time + ".")
        else:
            state.saved_events.append(
                SavedEvent(rec.title, planner, rec.category,
                           rec.price_estimate, rec.location,
                           save_day, save_time)
            )
            state.notice = ("Saved \"" + rec.title + "\" for " + save_day
                            + " at " + save_time + ". See it on the home page.")

    return recommendation_page(state, current_heading(state))


# Heading used on each results page
def current_heading(state: State) -> str:
    if state.current_route == "honeymoon_res":
        return "Honeymoon Recommendations"
    elif state.current_route == "party_res":
        return "Party Recommendations"
    return "Date Night Recommendations"


@route
def home_action(state: State, action: str,
                new_restore_phrase: str = "") -> Page:

    if new_restore_phrase.strip() != "":
        state.restore_phrase = new_restore_phrase.strip()

    if action == "save":
        return home(state)

    elif action == "honeymoon":
        return honeymoon(state)

    elif action == "party":
        return party(state)

    elif action == "datenight":
        return datenight(state)

    elif action == "panic":
        if state.restore_phrase.strip() == "":
            state.error_message = "Please input a secret phrase before using Discreet Exit."
            return home(state)
        state.previous_route = "home"
        return panic(state)


# Helper that builds one RecommendationData and adds it to the list
def add_rec(state: State, title: str, category: str, price: str,
            description: str, location: str, tip: str) -> None:
    state.recommendations.append(
        RecommendationData(title, category, price, description, location, tip)
    )


# HONEYMOON PLANNER
@route
def honeymoon(state: State) -> Page:
    state.current_route = "honeymoon"
    warning = state.error_message
    state.error_message = ""

    content = [
        page_title("Honeymoon Planner \u2665",
        "Let's find your dream honeymoon destination!"),
        card(
            section_label("What is your approximate budget?"),
        "\n",
            SelectBox("budget", [
        "Under $2,000",
        "$2,000-$5,000",
        "$5,000-$10,000",
        "Over $10,000"
            ], state.honeymoon_budget),
        "\n",
            section_label("What kind of trip sounds best?"),
        "\n",
            SelectBox("destination", [
        "🏖Tropical beach",
        "🛫Europe",
        "⛰️Mountains & adventure",
        "🏙City & culture",
        "🤔Not sure yet"
            ], state.honeymoon_dest)
        ),
        rose_button("Get Recommendations", "honeymoon_res"),
        rose_button("Home", "home"),
        rose_button("Discreet Exit", "go_panic")
    ]

    if warning != "":
        content.append(banner(warning))
        content.append(rose_button("Go to Home to Set Phrase", "home"))

    return themed_page(state, content)


@route
def honeymoon_res(state: State, budget: str,
                  destination: str) -> Page:

    state.current_route = "honeymoon_res"
    state.honeymoon_budget = budget
    state.honeymoon_dest = destination

    state.recommendations = []

    # Main recommendation based on budget
    if budget == "Under $2,000":
        add_rec(
            state,
        "San Juan and Culebra, Puerto Rico",
        "Tropical Beach",
        "Under $2,000",
        "Old San Juan's colorful streets and forts, great food, "
        "and a day trip to Flamenco Beach on the island of Culebra.",
        "Puerto Rico, Caribbean (about 3.5 hours by air from the "
        "Philadelphia area)",
        "U.S. citizens do not need a passport to visit, and hotels "
        "and flights are often cheaper from late spring to fall."
        )

    elif budget == "$2,000-$5,000":
        add_rec(
            state,
        "Cancun and the Riviera Maya, Mexico",
        "Tropical Beach",
        "$2,000-$5,000",
        "White-sand beaches, all-inclusive adult-only resorts, "
        "cenote swims, and Mayan ruins at Tulum and Chichen Itza.",
        "Quintana Roo, Mexico (about 4 hours by air from the "
        "Philadelphia area)",
        "Adults-only all-inclusive resorts keep the total cost "
        "predictable. Check hurricane season (June to November) "
        "before booking."
        )

    elif budget == "$5,000-$10,000":
        add_rec(
            state,
        "Santorini, Greece",
        "Europe",
        "$5,000-$10,000",
        "Whitewashed cliffside villages, sunset views over the "
        "caldera, wine tastings, and boat trips to volcanic hot "
        "springs.",
        "Cyclades Islands, Greece (roughly 11-13 hours by air "
        "with a connection)",
        "Go in May, June, or September for good weather with "
        "smaller crowds. Book a caldera-view room early."
        )

    else:
        add_rec(
            state,
        "Bora Bora, French Polynesia",
        "Luxury",
        "Over $10,000",
        "Overwater bungalows on a turquoise lagoon, private "
        "sunset cruises, snorkeling with rays, and spa dinners "
        "by the water.",
        "French Polynesia, South Pacific (a long trip, usually "
        "20+ hours with connections through the U.S. West Coast "
        "and Tahiti)",
        "Plan at least 8 to 10 nights so the long travel is "
        "worth it. Ask resorts about honeymoon packages."
        )

    # Extra recommendations based on trip style
    if destination == "🏖Tropical beach":
        add_rec(
            state,
        "Maui, Hawaii",
        "Tropical Beach",
        "$4,000-$8,000",
        "Beaches, a sunrise drive up Haleakala, the Road to "
        "Hana, whale watching in winter, and luaus.",
        "Hawaii, USA (roughly 11-13 hours by air with a connection)",
        "No passport needed. Rent a car to explore the island "
        "at your own pace."
        )
        add_rec(
            state,
        "Bali, Indonesia",
        "Tropical Beach",
        "$3,000-$7,000",
        "Jungle villas in Ubud, cliffside beach clubs, rice "
        "terraces, temples, and spa treatments at lower prices "
        "than many beach destinations.",
        "Bali, Indonesia (about 24+ hours by air with connections)",
        "Split your stay between Ubud for culture and a beach "
        "area like Uluwatu or Seminyak."
        )

    elif destination == "🛫Europe":
        add_rec(
            state,
        "Amalfi Coast, Italy",
        "Europe",
        "$5,000-$9,000",
        "Cliffside towns like Positano and Ravello, lemon groves, "
        "boat rides along the coast, and a day trip to Capri.",
        "Campania, Italy (about 9-10 hours by air, usually via "
        "Naples or Rome)",
        "May and September are warm, with fewer crowds than July "
        "and August."
        )
        add_rec(
            state,
        "Paris, France",
        "Europe",
        "$4,000-$8,000",
        "The Eiffel Tower, the Seine at night, museums, cafes, "
        "and a day trip to Versailles or Champagne.",
        "Paris, France (about 7-8 hours by air from the "
        "Philadelphia area)",
        "Book a Seine dinner cruise and museum tickets ahead "
        "of time."
        )

    elif destination == "⛰️Mountains & adventure":
        add_rec(
            state,
        "Swiss Alps, Switzerland",
        "Mountains",
        "$6,000-$10,000",
        "Scenic train rides, cable cars, lakeside towns like "
        "Interlaken and Lucerne, and the Matterhorn near Zermatt.",
        "Switzerland (about 8-9 hours by air, usually via Zurich "
        "or Geneva)",
        "A Swiss rail pass can simplify travel between towns."
        )
        add_rec(
            state,
        "Queenstown, New Zealand",
        "Adventure",
        "$6,000-$11,000",
        "Lakes, mountain scenery, wineries, hiking, and a day "
        "trip to Milford Sound.",
        "South Island, New Zealand (about 24+ hours by air with "
        "connections)",
        "The seasons are reversed, so December to February is "
        "summer there."
        )

    elif destination == "🏙City & culture":
        add_rec(
            state,
        "Tokyo and Kyoto, Japan",
        "City & Culture",
        "$5,000-$10,000",
        "Neon-lit Tokyo, quiet temples and tea houses in Kyoto, "
        "a bullet train between the two, and a traditional "
        "ryokan inn stay.",
        "Japan (about 14-16 hours by air with a connection)",
        "Spring cherry blossoms and fall leaves are popular, so "
        "book hotels early."
        )
        add_rec(
            state,
        "Barcelona, Spain",
        "City & Culture",
        "$3,500-$7,000",
        "Gaudi's architecture, tapas, beaches in the city, and "
        "day trips to wine country or Girona.",
        "Barcelona, Spain (about 8-9 hours by air)",
        "Book Sagrada Familia tickets ahead of time to skip "
        "long lines."
        )

    else:
        add_rec(
            state,
        "Italy: Rome, Florence & Venice",
        "Europe",
        "$5,000-$9,000",
        "A classic first-time trip with ancient sites, art, "
        "Tuscan food and wine, and gondola rides.",
        "Italy (about 9-10 hours by air)",
        "Use high-speed trains to travel between the cities."
        )
        add_rec(
            state,
        "Maui, Hawaii",
        "Tropical Beach",
        "$4,000-$8,000",
        "A mix of beaches, nature, great food, and relaxing "
        "resort stays, without needing a passport.",
        "Hawaii, USA (roughly 11-13 hours by air with a connection)",
        "A good pick if you cannot decide between relaxing and "
        "exploring."
        )

    return recommendation_page(state, "Honeymoon Recommendations")


# SURPRISE PARTY PLANNER
@route
def party(state: State) -> Page:
    state.current_route = "party"
    warning = state.error_message
    state.error_message = ""

    content = [
        page_title("Surprise Party Planner \u2665",
        "Let's organize a celebration in Newark!"),
        card(
            section_label("What type of celebration are you planning?"),
        "\n",
            SelectBox("party_type", [
        "🎂Birthday",
        "🎉Milestone Celebration",
        "🎁Holiday",
        "🎓Graduation"
            ], state.party_type),
        "\n",
            section_label("Who is the guest of honor?"),
        "\n",
            TextBox("party_honor_guest", state.party_honor_guest)
        ),
        rose_button("Get Party Ideas", "party_res"),
        rose_button("Home", "home"),
        rose_button("Discreet Exit", "go_panic")
    ]

    if warning != "":
        content.append(banner(warning))
        content.append(rose_button("Go to Home to Set Phrase", "home"))

    return themed_page(state, content)


@route
def party_res(state: State, party_type: str,
              party_honor_guest: str) -> Page:

    state.current_route = "party_res"
    state.party_type = party_type
    state.party_honor_guest = party_honor_guest

    state.recommendations = []

    if party_type == "🎂Birthday":
        add_rec(
            state,
        "Private Room at Klondike Kate's",
        "Birthday",
        "Custom quote",
        "A family-owned Main Street restaurant with three "
        "private rooms: the Parlor (up to 20 guests), the "
        "Rockwell Room (up to 25), and the Dawson Room (up to 80).",
        "Main Street, Newark, DE",
        "Call (302) 737-6100 to ask about custom menus and "
        "bar service."
        )
        add_rec(
            state,
        "Main Event Newark Party",
        "Birthday",
        "Package pricing varies",
        "Bowling, laser tag, a gravity ropes course, and over "
        "100 arcade games, with party packages.",
        "2900 Fashion Center Blvd, Newark, DE",
        "Pick a time slot where the guest of honor is likely to "
        "arrive on their own, so the surprise is easy to set up."
        )
        add_rec(
            state,
        "Lefty's Alley & Eats",
        "Birthday",
        "Varies",
        "A large venue with bowling, duckpin lanes, Topgolf "
        "Swing Suites, an arcade, ax throwing, and a "
        "restaurant and bar.",
        "College Square / The Grove shopping area, Newark, DE",
        "This is a newer location, so confirm the party room "
        "options with the venue directly."
        )

    elif party_type == "🎉Milestone Celebration":
        add_rec(
            state,
        "Group Dinner at Vita Nova",
        "Milestone",
        "Varies by group size",
        "A student-run fine-dining restaurant on the University "
        "of Delaware campus, with a French and American menu.",
        "University of Delaware campus, Newark, DE",
        "Ask about group reservations well ahead of time, "
        "since the restaurant follows the school's schedule."
        )
        add_rec(
            state,
        "Giordano's Newark Private Event Space",
        "Milestone",
        "Custom quote",
        "A 14,000-square-foot restaurant and sports bar with "
        "semi-private and private event rooms for larger groups.",
        "Newark, DE",
        "A good option if your guest list is large or you "
        "need flexible room sizes."
        )
        add_rec(
            state,
        "Deerfield Golf and Tennis Club",
        "Milestone",
        "Custom quote",
        "A banquet and special events facility on grounds "
        "next to White Clay Creek State Park.",
        "Deerfield, next to White Clay Creek State Park, Newark, DE",
        "Ask about photo spots on the grounds for the big reveal."
        )

    elif party_type == "🎁Holiday":
        add_rec(
            state,
        "Firebirds Private Dining Room",
        "Holiday",
        "Menu-based pricing",
        "A private dining room with customizable group menus. "
        "It seats about 60 banquet-style, and there is no "
        "charge to reserve the room.",
        "Christiana, Newark, DE",
        "Book early for December dates."
        )
        add_rec(
            state,
        "Dawson Room at Klondike Kate's",
        "Holiday",
        "Custom quote",
        "A historic Main Street room for up to 80 guests, "
        "with festive seasonal menus and a full bar.",
        "Main Street, Newark, DE",
        "Contact the event team at banquets@klondikekates.com "
        "to check holiday availability."
        )
        add_rec(
            state,
        "Skate Party at Patriot Ice Center",
        "Holiday",
        "Varies by group size",
        "An ice skating party with skate rentals and a party "
        "room, good for a winter holiday gathering.",
        "Patriot Ice Center, Newark, DE",
        "Confirm party room availability and skate times in advance."
        )

    else:
        add_rec(
            state,
        "Dinner at Home Grown Cafe",
        "Graduation",
        "Varies by group size",
        "A long-time Newark favorite with made-from-scratch "
        "food and options for many dietary needs.",
        "Main Street, Newark, DE",
        "Call ahead for a large reservation near graduation weekend."
        )
        add_rec(
            state,
        "Deerfield Banquet Facility",
        "Graduation",
        "Custom quote",
        "A banquet venue that hosts graduations, birthdays, "
        "and family events.",
        "Deerfield, next to White Clay Creek State Park, Newark, DE",
        "Book your date as early as possible, since spring "
        "weekends tend to fill up."
        )
        add_rec(
            state,
        "Main Event Newark",
        "Graduation",
        "Package pricing varies",
        "A casual group option with bowling, laser tag, and "
        "arcade games.",
        "2900 Fashion Center Blvd, Newark, DE",
        "Good for a relaxed party with a mixed age group."
        )

    return recommendation_page(state, "Party Recommendations")


# Builds the list of days an event can be planned for (default: today + next 29 days)
def get_day_options(num_days: int = 30) -> list[str]:
    options = []
    today = date.today()
    for offset in range(num_days):
        day = today + timedelta(days=offset)
        options.append(day.strftime("%A, %B ") + str(day.day) + day.strftime(", %Y"))
    return options


# Builds the list of times a date can start (11:00 AM - 10:30 PM, every 30 min)
def get_time_options() -> list[str]:
    options = []
    for hour in range(11, 23):
        for minute in (0, 30):
            t = time(hour, minute)
            options.append(t.strftime("%I:%M %p").lstrip("0"))
    return options


# DATE NIGHT PLANNER
@route
def datenight(state: State) -> Page:
    state.current_route = "datenight"
    warning = state.error_message
    state.error_message = ""

    day_options = get_day_options()
    time_options = get_time_options()

    # Keep the user's earlier choice if it is still a valid option
    selected_day = state.date_day if state.date_day in day_options else day_options[0]
    selected_time = state.date_time if state.date_time in time_options else "7:00 PM"

    content = [
        page_title("Date Night Planner \u2665",
        "Let's plan something special in Newark!"),
        card(
            section_label("What kind of date are you interested in?"),
        "\n",
            SelectBox("date_activity", [
        "🍽Romantic Dinner",
        "🥾Outdoor Adventure",
        "🍿Movie Night",
        "💃Fun Activity",
        "🧖Relaxing Evening"
            ], state.date_activity),
        "\n",
            section_label("What day are you planning for?"),
        "\n",
            SelectBox("date_day", day_options, selected_day),
        "\n",
            section_label("What time?"),
        "\n",
            SelectBox("date_time", time_options, selected_time)
        ),
        rose_button("Get Date Ideas", "datenight_res"),
        rose_button("Home", "home"),
        rose_button("Discreet Exit", "go_panic")
    ]

    if warning != "":
        content.append(banner(warning))
        content.append(rose_button("Go to Home to Set Phrase", "home"))

    return themed_page(state, content)


@route
def datenight_res(state: State, date_activity: str,
                  date_day: str, date_time: str) -> Page:

    state.current_route = "datenight_res"
    state.date_activity = date_activity
    state.date_day = date_day
    state.date_time = date_time
    state.date_timestamp = date_day + " at " + date_time
    state.save_day = date_day
    state.save_time = date_time

    state.recommendations = []

    if date_activity == "🍽Romantic Dinner":
        add_rec(
            state,
        "Vita Nova",
        "Romantic Dinner",
        "$50-$150 for two",
        "Elegant French and American dining run by University of "
        "Delaware hospitality students.",
        "University of Delaware campus, Newark, DE",
        "Check the restaurant's schedule, since it follows the "
        "academic calendar."
        )
        add_rec(
            state,
        "Taverna Rustic Italian",
        "Romantic Dinner",
        "$50-$120 for two",
        "A dim, cozy Italian restaurant on Main Street. Try "
        "the grilled artichoke to share, then pizza, pasta, "
        "or seafood.",
        "Main Street, Newark, DE",
        "Look for happy hour specials if you want to keep "
        "the cost down."
        )
        add_rec(
            state,
        "Home Grown Cafe",
        "Romantic Dinner",
        "$40-$100 for two",
        "A relaxed, award-winning spot known for made-from-scratch "
        "dishes like cauliflower wings and braised short rib "
        "mac and cheese.",
        "Main Street, Newark, DE",
        "Good for a casual, low-pressure date."
        )

    elif date_activity == "🥾Outdoor Adventure":
        add_rec(
            state,
        "White Clay Creek State Park Trails",
        "Outdoor",
        "$0-$20",
        "Over 35 miles of trails through woods and along the "
        "creek. Try the easy 1.9-mile PennDel Trail loop, or "
        "the short Cattail Pond walk at about 0.7 miles.",
        "750 Thompson Station Rd, Newark, DE",
        "Some trails close during hunting season, so check "
        "the park's website before you go."
        )
        add_rec(
            state,
        "Pomeroy Newark Rail Trail Walk",
        "Outdoor",
        "Free",
        "A flat, easy trail that connects the state park to "
        "the University of Delaware and downtown Newark.",
        "Newark, DE",
        "End the walk with coffee or dinner on Main Street."
        )
        add_rec(
            state,
        "Judge Morris Estate Walk",
        "Outdoor",
        "$0-$20",
        "A quiet 1790s manor house with trails in the "
        "surrounding park.",
        "White Clay Creek State Park, Newark, DE",
        "Bring a thermos for a cold-weather picnic."
        )

    elif date_activity == "🍿Movie Night":
        add_rec(
            state,
        "Cinemark at Christiana Mall",
        "Entertainment",
        "$25-$70 for two",
        "A large multi-screen theater, with shopping and "
        "restaurants in the mall for dinner before the show.",
        "Christiana Mall, Newark, DE",
        "Christiana Mall has no sales tax, so a little shopping "
        "before the movie can save money."
        )
        add_rec(
            state,
        "Resident Ensemble Players Theater Night",
        "Live Theater",
        "$30-$80 for two",
        "A professional theater company at the University of "
        "Delaware, a good alternative to a movie.",
        "University of Delaware, Newark, DE",
        "Buy tickets early for popular shows."
        )
        add_rec(
            state,
        "Dinner, Then a Show on Main Street",
        "Entertainment",
        "$40-$100 for two",
        "Eat at one of Main Street's many restaurants, then "
        "walk to a local show or take a short drive to the "
        "theater.",
        "Main Street, Newark, DE",
        "Make dinner reservations first, then pick showtimes."
        )

    elif date_activity == "💃Fun Activity":
        add_rec(
            state,
        "Main Event Newark",
        "Entertainment",
        "$40-$100 for two",
        "Bowling, multi-level laser tag, a gravity ropes "
        "course, and over 100 arcade games.",
        "2900 Fashion Center Blvd, Newark, DE",
        "Weeknights tend to be quieter."
        )
        add_rec(
            state,
        "Lefty's Alley & Eats",
        "Entertainment",
        "$40-$120 for two",
        "Bowling, duckpin bowling, Topgolf Swing Suites, "
        "ax throwing, darts, and a restaurant.",
        "College Square / The Grove shopping area, Newark, DE",
        "Try the duckpin lanes for something different."
        )
        add_rec(
            state,
        "Vince's Sports Center",
        "Entertainment",
        "$20-$60 for two",
        "A nine-hole golf course, two mini golf courses, "
        "batting cages, and an arcade.",
        "Newark, DE",
        "Best on a dry day, since much of it is outdoors."
        )
        add_rec(
            state,
        "Patriot Ice Center",
        "Entertainment",
        "$20-$50 for two",
        "Recreational ice skating, a classic winter date.",
        "Newark, DE",
        "Check public skate times before you go."
        )

    else:
        add_rec(
            state,
        "Harmony Spa",
        "Relaxation",
        "$100-$300 for two",
        "A day spa in the Pike Creek area that has been "
        "named a top day spa in Delaware.",
        "Pike Creek Valley, near Newark, DE",
        "Book treatments well in advance for weekends."
        )
        add_rec(
            state,
        "Hand & Stone Massage and Facial Spa",
        "Relaxation",
        "$100-$250 for two",
        "Massage and facial services in a calm setting.",
        "302 Suburban Dr, Newark, DE",
        "Call (302) 600-6145 to ask about booking two "
        "appointments at the same time."
        )
        add_rec(
            state,
        "Midnight Oil Brewing Company",
        "Relaxation",
        "$20-$60 for two",
        "A casual local brewery for a slow, low-key evening "
        "after a spa visit or a long week.",
        "Newark, DE",
        "Check the brewery's hours, since they vary by day."
        )

    return recommendation_page(state, "Date Night Recommendations")


# SHARED RECOMMENDATION PAGE
def recommendation_page(state: State, heading: str) -> Page:
    warning = state.error_message
    state.error_message = ""

    content = [
        page_title(heading,
        "Popular honeymoon destinations based on your answers"
                   if state.current_route == "honeymoon_res"
                   else "Ideas in and around Newark, DE, based on your answers"),
        small_font("Costs are rough estimates, so confirm prices and hours with each place.")
    ]

    # Show the chosen day and time on the date night results
    if state.current_route == "datenight_res":
        content.append(banner("Planned for: " + state.date_timestamp))

    notice = state.notice
    state.notice = ""
    if notice != "":
        content.append(banner(notice))

    # Day and time used when pressing "Save" on any of the ideas below
    day_options = get_day_options(365)
    time_options = get_time_options()
    selected_day = (state.save_day if state.save_day in day_options
                    else day_options[0])
    selected_time = (state.save_time if state.save_time in time_options
                     else "7:00 PM")
    content.append(
        card(
            section_label("Save an idea to your Saved Events"),
            "\n",
            small_font("Pick a day and time, then press Save on any idea "
                       "below. Change them to save another idea for a "
                       "different time."),
            "\n",
            section_label("Day"),
            "\n",
            SelectBox("save_day", day_options, selected_day),
            "\n",
            section_label("Time"),
            "\n",
            SelectBox("save_time", time_options, selected_time)
        )
    )

    # Loop through the list of RecommendationData objects
    for index, recommendation in enumerate(state.recommendations):
        content.append(
            card(
                change_color(Header(recommendation.title, 3), DEEP_ROSE),
                Span(bold("Category: "), recommendation.category),
        "\n",
                Span(bold("Estimated Cost: "), recommendation.price_estimate),
        "\n",
                Span(bold("Location: "), recommendation.location),
        "\n",
        "\n",
                recommendation.description,
        "\n",
        "\n",
                italic("Tip: " + recommendation.tip),
        "\n",
        "\n",
                rose_button("Save to Saved Events", "save_event",
                            [Argument("index", str(index))])
            )
        )

    # Go back to the planner page this result came from
    # (e.g. "honeymoon_res" -> "honeymoon")
    planner_route = state.current_route.replace("_res", "")
    content.append(rose_button("Go Back", planner_route))
    content.append(rose_button("Home", "home"))
    content.append(rose_button("Discreet Exit", "go_panic"))

    if warning != "":
        content.append(banner(warning))

    return themed_page(state, content)


# DISCREET EXIT
@route
def go_panic(state: State,
             budget: str = "",
             destination: str = "",
             party_type: str = "",
             party_honor_guest: str = "",
             date_activity: str = "",
             date_day: str = "",
             date_time: str = "",
             save_day: str = "",
             save_time: str = "") -> Page:

    # Save any information entered before leaving
    if save_day != "":
        state.save_day = save_day

    if save_time != "":
        state.save_time = save_time

    if budget != "":
        state.honeymoon_budget = budget

    if destination != "":
        state.honeymoon_dest = destination

    if party_type != "":
        state.party_type = party_type

    if party_honor_guest != "":
        state.party_honor_guest = party_honor_guest

    if date_activity != "":
        state.date_activity = date_activity

    if date_day != "":
        state.date_day = date_day

    if date_time != "":
        state.date_time = date_time

    # Prompt user if no secret phrase has been saved yet
    if state.restore_phrase.strip() == "":
        state.error_message = "Please input a secret phrase before using Discreet Exit."
        return return_to_current_page(state)

    state.previous_route = state.current_route
    state.current_route = "panic"

    return panic(state)


# ---------- WIKIPEDIA LOOK (used only by the discreet exit pages) ----------
WIKI_TEXT = "#202122"
WIKI_LINK = "#0645ad"
WIKI_GRAY = "#54595d"
WIKI_BORDER = "#a2a9b1"
WIKI_SANS = "Arial, Helvetica, sans-serif"
WIKI_SERIF = "'Linux Libertine', Georgia, Times, serif"


# Top bar with the site name and the article tabs
def wiki_topbar():
    tabs = Span(
        change_color("Article", WIKI_TEXT), "   ",
        change_color("Talk", WIKI_LINK), "      ",
        change_color("Read", WIKI_TEXT), "   ",
        change_color("Edit", WIKI_LINK), "   ",
        change_color("View history", WIKI_LINK)
    )
    bar = Div(
        change_text_font(change_text_size(Span("Wikipedia"), "24px"), WIKI_SERIF),
        change_color(small_font(Span("  The Free Encyclopedia")), WIKI_GRAY),
        "\n",
        change_text_size(tabs, "13px"),
        style_border_bottom="1px solid " + WIKI_BORDER,
        style_padding_bottom="6px",
        style_margin_bottom="12px"
    )
    return bar


# Big serif article title with a thin rule under it
def wiki_title(text: str):
    return Div(
        change_text_font(change_text_size(text, "30px"), WIKI_SERIF),
        style_border_bottom="1px solid " + WIKI_BORDER,
        style_margin_bottom="4px"
    )


# Small gray "From Wikipedia" line
def wiki_subtitle():
    return change_color(change_text_size(Div("From Wikipedia, the free encyclopedia"), "13px"), WIKI_GRAY)


# Section heading (like an h2)
def wiki_h2(text: str):
    return Div(
        change_text_font(change_text_size(text, "22px"), WIKI_SERIF),
        style_border_bottom="1px solid " + WIKI_BORDER,
        style_margin_top="18px",
        style_margin_bottom="8px"
    )


# Sub-section heading (like an h3)
def wiki_h3(text: str):
    return Div(
        bold(change_text_size(text, "17px")),
        style_margin_top="14px",
        style_margin_bottom="4px"
    )


# Italic indented "Main article: ..." note
def hatnote(text: str):
    return Div(italic(text), style_padding_left="24px", style_margin_bottom="6px")


# Contents box like the one under the intro of a Wikipedia article
def wiki_toc():
    sections = [
        ("History", []),
        ("Common designs", ["Angular contact", "Axial", "Deep-groove",
        "Preloaded pairs"]),
        ("Construction types", ["Conrad", "Slot-fill", "Relieved race",
        "Fractured race", "Wire race", "Rows",
        "Flanged", "Caged",
        "Hybrid ball bearings using ceramic balls",
        "Fully ceramic bearings", "Self-aligning"]),
        ("Operating conditions", ["Lifespan", "Failure modes", "Maximum load",
        "Lubrication", "Direction of load",
        "Avoiding undesirable axial load", "Fit",
        "Avoiding torsional loads"]),
        ("Applications", []),
        ("Designation", [])
    ]
    lines = [bold("Contents")]
    for i, (name, subs) in enumerate(sections, start=1):
        lines.append(Div(change_color(str(i) + "  " + name, WIKI_LINK)))
        for j, sub in enumerate(subs, start=1):
            lines.append(Div(change_color(str(i) + "." + str(j) + "  " + sub, WIKI_LINK),
                             style_padding_left="22px"))
    return Div(
        *lines,
        style_background_color="#f8f9fa",
        style_border="1px solid " + WIKI_BORDER,
        style_padding="8px 14px",
        style_margin="10px 0",
        style_width="fit-content",
        style_font_size="13px"
    )


# Edit box at the bottom of the article (this is where the secret phrase goes)
def wiki_edit_box(state: State):
    return Div(
        bold("Add Info / Propose Edit:"),
        "\n",
        TextBox("wikipedia_feedback", state.wikipedia_feedback),
        Button("Submit Edit", "panic_action",
               style_background_color="#36c", style_color="white"),
        style_background_color="#f8f9fa",
        style_border="1px solid " + WIKI_BORDER,
        style_padding="10px 14px",
        style_margin_top="24px"
    )


# Turns blank-line-separated text blocks into separate paragraphs
def wiki_body(items: list) -> list:
    out = []
    for item in items:
        if isinstance(item, str) and "\n\n" in item:
            for para in item.split("\n\n"):
                para = " ".join(para.split())
                if para != "":
                    out.append(Div(para, style_margin_bottom="8px"))
        else:
            out.append(item)
    return out


# Wraps a list of components in the Wikipedia page look
def wiki_page(state: State, body: list) -> Page:
    return Page(state, [
        Div(
            wiki_topbar(),
            *wiki_body(body),
            style_background_color="white",
            style_color=WIKI_TEXT,
            style_font_family=WIKI_SANS,
            style_font_size="14px",
            style_line_height="1.6",
            style_max_width="960px",
            style_margin="0 auto",
            style_padding="10px 20px"
        )
    ])


# DISCREET BALL BEARING PAGE
@route
def panic(state: State) -> Page:
    state.current_route = "panic"

    body = [
        wiki_title("Ball bearing"),
        wiki_subtitle(),
        "A ball bearing is a type of rolling-element bearing that uses balls to maintain",
        "the separation between the bearing races.\n",
        "The purpose of a ball bearing is to reduce rotational friction and support radial and axial loads.",
        "It achieves this by using at least two races to contain the balls and transmit the loads through the balls.",
        "In most applications, one race is stationary and the other is attached to the rotating assembly (e.g., a hub or shaft).",
        "As one of the bearing races rotates it causes the balls to rotate as well. Because the balls are rolling,",
        "they have a much lower coefficient of friction than if two flat surfaces were sliding against each other.\n",
        "Ball bearings tend to have lower load capacity for their size than other kinds of rolling-element bearings due to",
        "the smaller contact area between the balls and races. However, they can tolerate some misalignment of the inner and",
        "outer races.\n"
        "Common ball bearing designs include angular contact, axial, deep-groove, and preloaded pairs. The balls in ball bearings",
        "can also be configured in various ways.",
        "Ball bearings are used in a wide range of applications, some of which include skateboards and centrifugal pumps.\n",
        "\n",
        wiki_toc(),
        wiki_h2("History"),
        hatnote("Main article: History of bearings"),
        "Although bearings had been developed since ancient times, the first modern recorded patent on ball bearings",
        "was awarded to Philip Vaughan,",
        "a Welsh inventor and ironmaster who created the first design for a ball bearing in Carmarthen in 1794. His is",
        "the first modern ball-bearing design, with the ball running along a groove in the axle assembly.[1]\n",
        "Jules Suriray, a Parisian bicycle mechanic, designed the first radial style ball bearing in 1869,[2] which was",
        "then fitted to the winning bicycle ridden by James Moore in the world's first bicycle road race, Paris-Rouen,",
        "in November 1869.[3]\n",
        "\n",
        wiki_h2("Common designs"),
        "There are several common designs of ball bearing, each offering various performance trade-offs. They can be made",
        "from many different materials, including stainless steel, chrome steel, and ceramic",
        "(silicon nitride, Si3N4). A hybrid ball bearing is a bearing with ceramic balls and metal races.\n",
        "\n",
        wiki_h3("Angular contact"),
        "An angular contact ball bearing uses axially asymmetric races. An axial load passes in a straight line through",
        "the bearing, whereas a radial load takes an oblique path that acts to separate the races axially. So, the angle",
        "of contact",
        "on the inner race is the same as that on the outer race. Angular contact bearings better support combined",
        "loads (loading in both the radial and axial directions) and the contact angle of the bearing should be matched",
        "to the relative",
        "proportions of each. The larger the contact angle (typically in the range 10 to 45 degrees), the higher the axial",
        "load supported, but the lower the radial load. In high-speed applications, such as turbines, jet engines, and dentistry",
        "equipment,",
        "the centrifugal forces generated by the balls change the contact angle at the inner and outer race. Ceramics such",
        "as silicon nitride are now regularly used in such applications due to their low density (40% of steel). These",
        "materials significantly",
        "reduce centrifugal force and function well in high temperature environments. They also tend to wear in a",
        "similar way to bearing steel—rather than cracking or shattering like glass or porcelain. Most bicycles use",
        "angular-contact bearings in the headsets",
        "because the forces on these bearings are in both the radial and axial direction.\n",
        "\n",
        wiki_h3("Axial"),
        "An axial or thrust ball bearing uses side-by-side races. An axial load is transmitted directly through the bearing,",
        "while a radial load is poorly supported and tends to separate the races, so that a larger radial load is likely to",
        "damage the bearing.\n",
        "\n",
        wiki_h3("Deep-groove"),
        "In a deep-groove radial bearing, the race dimensions are close to the dimensions of the balls that run in it.",
        "Deep-groove bearings support higher loads than a shallower groove. Like angular contact bearings, deep-groove",
        "bearings support both radial and",
        "axial loads, but without a choice of contact angle to allow choice of relative proportion of these load capacities.\n",
        "\n",
        wiki_h3("Preloaded pairs"),
        "The above basic types of bearings are typically applied in a method of preloaded pairs, where two individual",
        "bearings are rigidly fastened along a rotating shaft to face each other. This improves the axial runout by",
        "taking up (preloading) the necessary",
        "slight clearance between the bearing balls and races. Pairing also provides an advantage of evenly distributing",
        "the loads, nearly doubling the total load capacity compared to a single bearing. Angular contact bearings are",
        "almost always used in",
        "opposing pairs: the asymmetric design of each bearing supports axial loads in only one direction, so an opposed",
        "pair is required if the application demands support in both directions. The preloading force must be designed and assembled carefully,",
        "because it deducts from the axial force capacity of the bearings and can damage bearings if applied excessively.",
        "The pairing mechanism may simply face the bearings together directly, or separate them with a shim, bushing, or",
        "shaft feature.\n",
        "\n",
        wiki_h2("Construction types"),
        "\n",
        wiki_h3("Conrad"),
        "The Conrad-style ball bearing is named after its inventor, Robert Conrad, who was awarded British patent 12,206",
        "in 1903 and U.S. patent 822,723 in 1906. These bearings are assembled by placing the inner ring into an eccentric",
        "position relative to",
        "the outer ring, with the two rings in contact at one point, resulting in a large gap opposite the point of contact.",
        "The balls are inserted through the gap and then evenly distributed around the bearing assembly, causing the rings",
        "to become concentric.",
        "Assembly is completed by fitting a cage to the balls to maintain their positions relative to each other. Without",
        "the cage, the balls would eventually drift out of position during operation, causing the bearing to fail. The",
        "cage carries no load and serves",
        "only to maintain ball position. Conrad bearings have the advantage that they are able to withstand both radial",
        "and axial loads but have the disadvantage of lower load capacity due to the limited number of balls that can",
        "be loaded into the bearing assembly.",
        "Probably the most familiar industrial ball bearing is the deep-groove Conrad style. The bearing is used in",
        "most of the mechanical industries.\n",
        "\n",
        wiki_h3("Slot-fill"),
        "In a slot-fill radial bearing, the inner and outer races are notched on one face so that when the notches are",
        "aligned, balls can be slipped in the resulting slot to assemble the bearing. A slot-fill bearing has the",
        "advantage that more balls can be assembled",
        "(even allowing a full complement design), resulting in a higher radial load capacity than a Conrad bearing",
        "of the same dimensions and material type. However, a slot-fill bearing cannot carry a significant axial load,",
        "and the slots cause a discontinuity in the",
        "races that can have a small but adverse effect on strength.\n"
        "\n",
        wiki_h3("Relieved race"),
        "Relieved race ball bearings are 'relieved' as the name suggests by having either the OD of the inner ring",
        "reduced on one side, or the ID of the outer ring increased on one side. This allows a greater number of",
        "balls to be assembled into either the inner or outer race,",
        "and then press fit over the relief. Sometimes the outer ring will be heated to facilitate assembly.",
        "Like the slot-fill construction, relieved race construction allows a greater number of balls than Conrad",
        "construction, up to and including full complement, and the extra",
        "ball count gives extra load capacity. However, a relieved race bearing can only support significant axial",
        "loads in one direction ('away from' the relieved race).\n",
        "\n",
        wiki_h3("Fractured race"), 
        "Another way of fitting more balls into a radial ball bearing is by radially 'fracturing' (slicing) one of",
        "the rings all the way through, loading the balls in, re-assembling the fractured portion, and then using a",
        "pair of steel bands to hold the fractured ring sections",
        "together in alignment. Again, this allows more balls, including full ball complement, however unlike with",
        "either slot fill or relieved race constructions, it can support significant axial loading in either direction.\n",
        "\n",
        wiki_h3("Wire race"),
        "Four wire rings are arranged in a square, to contact four points on a ball bearing. The wire rings are bearing",
        "steel and are ground smooth where they contact the bearing balls. The wires cannot support bearing loads directly,",
        "so are placed in a housing.",
        "The housing may be a material which is not suitable for bearings but has other useful properties.",
        "For example, wires in an aluminum housing may be lighter than a similar-size bearing made entirely of steel.",
        "There are also 3-wire, linear, and other wire race bearings.\n",
        "\n",
        wiki_h3("Rows"),
        "There are two row designs: single-row bearings and double-row bearings. Most ball bearings are a single-row design,",
        "which means there is one row of bearing balls. This design works with radial and thrust loads.[4] A double-row",
        "design has two rows of bearing balls.",
        "Advantages of double-row bearings as compared to single-row include that they can bear radial and axial loads",
        "in both directions. Double-row angular contact ball bearings have a steep mounting, which also can bear tilting",
        "effects. Other advantages of double-row bearings are",
        "their rigidity and compactness. Their disadvantage is they need better alignment than single-row bearings.\n",
        wiki_h3("Flanged"),
        "Bearings with a flange on the outer ring simplify axial location. The housing for such bearings can consist of",
        "a through-hole of uniform diameter, but the entry face of the housing (which may be either the outer or inner face)",
        "must be machined truly normal to the hole axis.",
        "However, such flanges are very expensive to manufacture. A more cost-effective arrangement of the bearing outer",
        "ring, with similar benefits, is a snap ring groove at either or both ends of the outside diameter. The snap",
        "ring assumes the function of a flange.\n"
        "\n",
        wiki_h3("Caged"),
        "Cages are typically used to secure the balls in a Conrad-style ball bearing. In other construction types",
        "they may decrease the number of balls depending on the specific cage shape, and thus reduce the load capacity.",
        "Without cages the tangential position is stabilized by",
        "sliding of two convex surfaces on each other. With a cage the tangential position is stabilized by a sliding",
        "of a convex surface in a matched concave surface, which avoids dents in the balls and has lower friction. Caged",
        "roller bearings were invented by John Harrison in",
        "the mid-18th century as part of his work on chronographs.[5]\n",
        "\n",
        wiki_h3("Hybrid ball bearings using ceramic balls"),
        "Ceramic bearing balls can weigh up to 40% less than steel ones, depending on size and material. This reduces",
        "centrifugal loading and skidding, so hybrid ceramic bearings can operate 20% to 40% faster than conventional bearings.",
        "This means that the outer race groove exerts",
        "less force inward against the ball as the bearing spins. This reduction in force reduces the friction and",
        "rolling resistance. The lighter balls allow the bearing to spin faster, and uses less power to maintain its",
        "speed. The ceramic balls are typically harder than the race.",
        "Due to wear, with time they will form a groove in the race. This is preferable to the balls wearing which",
        "would leave them with possible flat spots significantly harming performance. While ceramic hybrid bearings",
        "use ceramic balls in place of steel ones, they are constructed",
        "with steel inner and outer rings; hence the hybrid designation. While the ceramic material itself is stronger",
        "than steel, it is also stiffer, which results in increased stresses on the rings, and hence decreased load",
        "capacity. Ceramic balls are electrically insulating,",
        "which can prevent 'arcing' failures if current should be passed through the bearing. Ceramic balls can",
        "also be effective in environments where lubrication may not be available (such as in space applications).",
        "In some settings only a thin coating of ceramic is used over a metal ball bearing.\n",
        "\n",
        wiki_h3("Fully ceramic bearings"),
        "These bearings make use of both ceramic balls and race. These bearings are impervious to corrosion and",
        "rarely require lubrication if at all. Due to the stiffness and hardness of the balls and race these bearings",
        "are noisy at high speeds. The stiffness of the ceramic makes these bearings",
        "brittle and liable to crack under load or impact. Because both ball and race are of similar hardness,",
        "wear can lead to chipping at high speeds of both the balls and the race, which can cause sparking.\n"
        "\n",        
        wiki_h3("Self-aligning"),
        "Self-aligning ball bearings, such as the Wingqvist bearing shown in the picture, are constructed with the",
        "inner ring and ball assembly contained within an outer ring that has a spherical raceway. This construction",
        "allows the bearing to tolerate a small angular misalignment resulting from",
        "shaft or housing deflections or improper mounting. The bearing was used mainly in bearing arrangements with",
        "very long shafts, such as transmission shafts in textile factories.[6] One drawback of the self-aligning ball",
        "bearings is a limited load rating, as the outer raceway has very low",
        "osculation (its radius is much larger than the ball radius). This led to the invention of the spherical roller",
        "bearing, which has a similar design, but uses rollers instead of balls. The spherical roller thrust bearing is",
        "another invention derived from the findings by Wingqvist.\n",
        "\n",
        wiki_h2("Operating conditions"),
        "\n",
        wiki_h3("Lifespan"),
        hatnote("Further information: Rolling-element bearing § Bearing failure"),
        "The calculated life for a bearing is based on the load it carries and its operating speed. The industry standard",
        "usable bearing lifespan is inversely proportional to the bearing load cubed.[citation needed] Nominal maximum load",
        "of a bearing, is for a lifespan of 1 million rotations,",
        "which at 50 Hz (i.e., 3000 RPM) is a lifespan of 5.5 working hours. 90% of bearings of that type have at least",
        "that lifespan, and 50% of bearings have a lifespan at least 5 times as long.[7]\n",
        "The industry standard life calculation is based upon the work of Lundberg and Palmgren performed in 1947. The formula",
        "assumes the life to be limited by metal fatigue and that the life distribution can be described by a Weibull",
        "distribution. Many variations of the formula exist that",
        "include factors for material properties, lubrication, and loading. Factoring for loading may be viewed as a",
        "tacit admission that modern materials demonstrate a different relationship between load and life than Lundberg",
        "and Palmgren determined .[7]\n",
        "\n",
        wiki_h3("Failure modes"),
        "If a bearing is not rotating, maximum load is determined by force that causes plastic deformation of elements",
        "or raceways. The indentations caused by the elements can concentrate stresses and generate cracks at the components.",
        "Maximum load for not or very slowly rotating bearings is called \"static\" maximum load.[7]\n",
        "Also, if a bearing is not rotating, oscillating forces on the bearing can cause impact damage to the bearing race",
        "or the rolling elements, known as brinelling. A second lesser form called false brinelling occurs if the bearing",
        "only rotates across a short arc and pushes lubricant out away from the rolling elements.\n",
        "For a rotating bearing, the dynamic load capacity indicates the load to which the bearing endures 1,000,000 cycles.\n",
        "If a bearing is rotating, but experiences heavy load that lasts shorter than one revolution, static max load",
        "must be used in computations, since the bearing does not rotate during the maximum load.[7]\n",
        "If a sideways torque is applied to a deep groove radial bearing, an uneven force in the shape of an ellipse",
        "is applied on the outer ring by the rolling elements, concentrating in two regions on opposite sides of the",
        "outer ring. If the outer ring is not strong enough,",
        "or if it is not sufficiently braced by the supporting structure, the outer ring will deform into an oval shape",
        "from the sideways torque stress, until the gap is large enough for the rolling elements to escape. The inner ring",
        "then pops out and the bearing structurally collapses.\n",
        "A sideways torque on a radial bearing also applies pressure to the cage that holds the rolling elements at equal",
        "distances, due to the rolling elements trying to all slide together at the location of highest sideways torque.",
        "If the cage collapses or breaks apart, the rolling elements group together,",
        "the inner ring loses support, and may pop out of the center.\n",
        "\n",

        wiki_h3("Maximum load"),
        "In general, maximum load on a ball bearing is proportional to outer diameter of the bearing times the width of the",
        "bearing (where width is measured in direction of axle).[7]\n",
        "Bearings have static load ratings. These are based on not exceeding a certain amount of plastic deformation",
        "in the raceway. These ratings may be exceeded by a large amount for certain applications.\n",
        "\n",

        wiki_h3("Lubrication"),
        "For a bearing to operate properly, it needs to be lubricated. In most cases the lubricant is based on",
        "elastohydrodynamic effect (by oil or grease) but working at extreme temperatures dry lubricated bearings",
        "are also available.\n",
        "For a bearing to have its nominal lifespan at its nominal maximum load, it must be lubricated with a",
        "lubricant (oil or grease) that has at least the minimum dynamic viscosity (usually denoted with the",
        "Greek letter ν) recommended for that bearing.[7]\n",
        "The recommended dynamic viscosity is inversely proportional to diameter of bearing.[7]\n",
        "The recommended dynamic viscosity decreases with rotating frequency. As a rough indication:",
        "for less than 3000 RPM, recommended viscosity increases with factor 6 for a factor 10 decrease in speed,",
        "and for more than 3000 RPM, recommended viscosity decreases with factor 3 for a factor 10 increase in speed.[7]\n",
        "For a bearing where average of outer diameter of bearing and diameter of axle hole is 50 mm, and that is",
        "rotating at 3000 RPM, recommended dynamic viscosity is 12 mm2/s.[7]\n",
        "Note that dynamic viscosity of oil varies strongly with temperature: a temperature increase of 50–70 °C",
        "causes the viscosity to decrease by factor 10.[7]\n",
        "If the viscosity of lubricant is higher than recommended, lifespan of bearing increases, roughly proportional",
        "to square root of viscosity. If the viscosity of the lubricant is lower than recommended, the lifespan of the",
        "bearing decreases, and by how much depends on which type of oil being used. For oils with EP",
        "('extreme pressure') additives, the lifespan is proportional to the square root of dynamic viscosity, just as",
        "it was for too high viscosity, while for ordinary oils lifespan is proportional to the square of the viscosity",
        "if a lower-than-recommended viscosity is used.[7]\n",
        "Lubrication can be done with a grease, which has advantages that grease is normally held within the bearing",
        "releasing the lubricant oil as it is compressed by the balls. It provides a protective barrier for the",
        "bearing metal from the environment, but has disadvantages that this grease must be replaced periodically,",
        "and maximum load of bearing decreases (because if bearing gets too warm, grease melts and runs out of bearing).",
        "Time between grease replacements decreases very strongly with diameter of bearing: for a 40 mm bearing, grease",
        "should be replaced every 5000 working hours, while for a 100 mm bearing it should be replaced every 500 working",
        "hours.[7]\n",
        "Lubrication can also be done with an oil, which has advantage of higher maximum load, but needs some way to keep",
        "oil in bearing, as it normally tends to run out of it. For oil lubrication it is recommended that for applications",
        "where oil does not become warmer than 50 °C, oil should be replaced once a year, while for",
        "applications where oil does not become warmer than 100 °C, oil should be replaced 4 times per year. For car engines,",
        "oil becomes 100 °C but the engine has an oil filter to maintain oil quality; therefore, the oil is usually changed",
        "less frequently than the oil in bearings.[7]\n",
        "If the bearing is used under oscillation, oil lubrication should be preferred.[8] If grease lubrication is",
        "necessary, the composition should be adapted to the parameters that occur. Greases with a high bleeding rate",
        "and low base oil viscosity should be preferred if possible.[9]\n",
        "\n",

        wiki_h3("Direction of load"),
        "Most bearings are meant for supporting loads perpendicular to axle (\"radial loads\"). Whether they can also",
        "bear axial loads, and if so, how much, depends on the type of bearing. Thrust bearings (commonly found on lazy",
        "susans) are specifically designed for axial loads.[7]\n",
        "For single-row deep-groove ball bearings, SKF's documentation says that maximum axial load is circa 50% of maximum",
        "radial load, but it also says that \"light\" and/or \"small\" bearings can take axial loads that are 25% of maximum",
        "radial load.[7]\n",
        "For single-row edge-contact ball bearings, axial load can be about 2 times max radial load, and for cone-bearings",
        "maximum axial load is between 1 and 2 times maximum radial load.[7]\n",
        "Often Conrad-style ball bearings will exhibit contact ellipse truncation under axial load. That means that either",
        "the ID of the outer ring is large enough, or the OD of the inner ring is small enough, so as to reduce the area",
        "of contact between the balls and raceway. When this is the case, it can significantly increase",
        "the stresses in the bearing, often invalidating rules of thumb regarding relationships between radial and axial",
        "load capacity. With construction types other than Conrad, one can further decrease the outer ring ID and increase",
        "the inner ring OD to guard against this.\n",
        "If both axial and radial loads are present, they can be added vectorially, to result in the total load on bearing,",
        "which in combination with nominal maximum load can be used to predict lifespan.[7] However, in order to correctly",
        "predict the rating life of ball bearings the ISO/TS 16281 should be used with the help of a calculation software.\n",
        "\n",

        wiki_h3("Avoiding undesirable axial load"),
        "The part of a bearing that rotates (either axle hole or outer circumference) must be fixed, while for a part that",
        "does not rotate this is not necessary (so it can be allowed to slide). If a bearing is loaded axially, both sides",
        "must be fixed.[7]\n",
        "If an axle has two bearings, and temperature varies, axle shrinks or expands, therefore it is not admissible for",
        "both bearings to be fixed on both their sides, since expansion of axle would exert axial forces that would destroy",
        "these bearings. Therefore, at least one of the bearings must be able to slide.[7]\n",
        "A 'freely sliding fit' is one where there is at least a 4 μm clearance, presumably because surface-roughness of a",
        "surface made on a lathe is normally between 1.6 and 3.2 μm.[7]\n",
        "\n",

        wiki_h3("Fit"),
        "Bearings can withstand their maximum load only if the mating parts are properly sized. Bearing manufacturers supply",
        "tolerances for the fit of the shaft and the housing so that this can be achieved. The material and hardness may also",
        "be specified.[7]\n",
        "Fittings that are not allowed to slip are made to diameters that prevent slipping and consequently the mating surfaces",
        "cannot be brought into position without force. For small bearings this is best done with a press because tapping with",
        "a hammer damages both bearing and shaft, while for large bearings the",
        "necessary forces are so great that there is no alternative to heating one part before fitting, so that thermal",
        "expansion allows a temporary sliding fit.[7]\n",
        "\n",

        wiki_h3("Avoiding torsional loads"),
        "If a shaft is supported by two bearings, and the center-lines of rotation of these bearings are not the same,",
        "then large forces are exerted on the bearing, which may destroy it. Some very small amount of misalignment",
        "is acceptable, and how much depends on type of bearing.",
        "For bearings that are specifically made to be 'self-aligning', acceptable misalignment is between 1.5 and",
        "3 degrees of arc. Bearings that are not designed to be self-aligning can accept misalignment of only",
        "2–10 minutes of arc (0.033-0.166 degrees) .[7]\n",
        "\n",

        wiki_h2("Applications"),

        change_text_size(italic("A ball bearing for skateboard wheels with a plastic cage"), "12px"),
        "In general, ball bearings are used in most applications that involve moving parts. Some of these",
        "applications have specific features and requirements:",
        BulletedList([
        "Computer fan and spinning device bearings used to be highly spherical and were said to be the best spherical manufactured shapes, but this is no longer true for hard disk drive, and more and more are being replaced with fluid bearings.",
        "In horology, the Jean Lassale company designed a watch movement that used ball bearings to reduce the thickness of the movement. Using 0.20 mm balls, the Calibre 1200 was only 1.2 mm thick, which still is the thinnest mechanical watch movement.[10]",
        "Aerospace bearings are used in many applications on commercial, private and military aircraft including pulleys, gearboxes and jet engine shafts. Materials include M50 tool steel (AMS6491), carbon chrome steel (AMS6444), the corrosion resistant AMS5930, 440C stainless steel, silicon nitride (ceramic) and titanium carbide-coated 440C.",
        "A skateboard wheel contains two bearings, which are subject to both axial and radial time-varying loads. Most commonly bearing 608-2Z is used (a deep groove ball bearing from series 60 with 8 mm bore diameter)",
        "Many yo-yos, ranging from beginner to professional or competition grade, incorporate ball bearings.",
        "Many fidget spinner toys use multiple ball bearings to add weight, and to allow the toy to spin.",
        "In centrifugal pumps.",
        "Railroad locomotive axle journals. Side rod action of newest high speed steam locomotives before railroads were converted to diesel engines."
        ]),

        wiki_h2("Designation"),
        hatnote("Main article: Rolling-element bearing § Designation"),
        "The ball size increases as the series increases, for any given inner diameter or outer diameter (not both). The larger the ball the greater the load carrying capacity. Series 200 and 300 are the most common.\n",
        "\n",
        wiki_edit_box(state),
    ]

    return wiki_page(state, body)


@route
def panic_action(state: State, wikipedia_feedback: str) -> Page:
    state.wikipedia_feedback = wikipedia_feedback

    # Check if the text entered into the edit box matches the secret restore phrase
    if wikipedia_feedback == state.restore_phrase and wikipedia_feedback != "":
        # Clear the box so the secret phrase isn't left sitting in the state
        state.wikipedia_feedback = ""

        # Restore the route so the Go Back button points to the right planner
        state.current_route = state.previous_route

        if state.previous_route == "honeymoon":
            return honeymoon(state)

        elif state.previous_route == "honeymoon_res":
            return honeymoon_res(
                state,
                state.honeymoon_budget,
                state.honeymoon_dest
            )

        elif state.previous_route == "party":
            return party(state)

        elif state.previous_route == "party_res":
            return recommendation_page(
                state, "Party Recommendations"
            )

        elif state.previous_route == "datenight":
            return datenight(state)

        elif state.previous_route == "datenight_res":
            return datenight_res(
                state,
                state.date_activity,
                state.date_day,
                state.date_time
            )

        else:
            return home(state)

    # If it doesn't match (or is blank), show the fake Wikipedia edit confirmation
    else:
        return wiki_page(state, [
            wiki_title("The History of Ball Bearings"),
            wiki_subtitle(),
        "\n",
        "Please wait 3-5 business days for the page to be updated",
        "\n",
            Button("Return", "panic",
                   style_background_color="#36c", style_color="white")
        ])
    
set_website_title("OTR Planning")
set_site_information(
    author="Carter Hoatson",
    description="An secret event planner that caters to a diverse amount of things and has a panic button to hide the screen from anyone that you want",
    sources="BlockPy Workbook, Claude, Gemini",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
# START THE WEBSITE
start_server(State(
    current_route="home",
    previous_route="home",
    restore_phrase="",
    phrase_attempt="",
    wikipedia_feedback="",
    honeymoon_budget="Under $2,000",
    honeymoon_dest="🤔Not sure yet",
    party_type="🎂Birthday",
    party_honor_guest="",
    date_activity="🍽Romantic Dinner",
    date_timestamp="",
    recommendations=[],
    error_message="",
    saved_events=[]
))
