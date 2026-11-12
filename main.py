from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

@dataclass
class Material:
    """
    A material a beam can be made of.
 
    Attributes:
        name (str): the material's name
        youngs_modulus (float): stiffness E, in GPa
        yield_strength (float): stress where it permanently bends, in MPa
    """
    name: str
    youngs_modulus: float
    yield_strength: float
 
 
@dataclass
class State:
    """
    The current state of the Beam Bending Sim.
 
    Attributes:
        length (float): beam length in meters
        load (float): force at the middle of the beam in newtons
        width (float): cross section width in mm
        height (float): cross section height in mm
        materials (list[Material]): the materials to compare side by side
        status (str): the message shown the user
        only_passing (bool): true if the results should hide failing materials
    """
    length: float
    load: float
    width: float
    height: float
    materials: list[Material]
    status: str
    only_passing: bool
 
 
TEST_MATERIALS = [Material("Steel", 200, 250)]
 
 
def moment_of_inertia(width: float, height: float) -> float:
    """
    Calculates the moment of inertia of a rectangular cross section.
 
    Args:
        width (float): cross section width in mm
        height (float): cross section height in mm
 
    Returns:
        float: moment of inertia in m^4
    """
    width_m = width / 1000  # width in meters
    height_m = height / 1000  # height in meters
    return width_m * height_m ** 3 / 12
 
TEST_INERTIA = moment_of_inertia(50, 100)
assert_equal(TEST_INERTIA, 0.0000041666666666666)

 
def max_deflection(load: float, length: float, youngs_modulus: float,
                   inertia: float) -> float:
    """
    Calculates the max deflection of a supported beam with a load
    in the middle using deflection = P * L^3 / (48 * E * I).
 
    Args:
        load (float): force in N
        length (float): beam length in m
        youngs_modulus (float): stiffness E in GPa
        inertia (float): moment of inertia in m^4
 
    Returns:
        float: max deflection in mm
    """
    e_pa = youngs_modulus * 10**9
    deflection_m = (load * (length**3)) / (48 * e_pa * inertia)
    return deflection_m * 1000
 
assert_equal(max_deflection(1000, 2, 200, TEST_INERTIA), 0.2)

 
def max_stress(load: float, length: float, height: float,
               inertia: float) -> float:
    """
    Calculates the max bending stress in the beam using
    stress = M * c / I, where M = P * L / 4 and c = height / 2.
 
    Args:
        load (float): force in N
        length (float): beam length in m
        height (float): cross section height in mm
        inertia (float): moment of inertia in m^4
 
    Returns:
        float: max stress in MPa
    """
    moment = load * length / 4
    c = (height / 1000) / 2
    stress_pa = moment * c / inertia
    return stress_pa / 10**6

assert_equal(max_stress(1000, 2, 100, TEST_INERTIA), 6.0)
  
 
def safety_factor(yield_strength: float, stress: float) -> float:
    """
    Calculates the safety factor which is how many times stronger
    or weaker the material is than it needs to be.
 
    Args:
        yield_strength (float): yield strength in MPa
        stress (float): max stress in MPa
 
    Returns:
        float: the safety factor (above 1 means it passes)
    """
    return yield_strength / stress

assert_equal(safety_factor(40, 80), 0.5)

  
def is_positive_number(text: str) -> bool:
    """
    Checks whether text is a positive number, like "2" or "2.5".

    Args:
        text (str): the text the user typed

    Returns:
        bool: True if text is a positive number, False otherwise
    """
    if text.replace(".", "", 1).isdigit():
        return float(text) > 0
    return False

assert_equal(is_positive_number("2.5"), True)
assert_equal(is_positive_number("0"), False)
assert_equal(is_positive_number("abc"), False)


def recommendation(best_name: str, best_sf: float) -> str:
    """
    Builds a short recommendation based on the best material.

    Args:
        best_name (str): name of the material with the highest safety factor
        best_sf (float): that material's safety factor

    Returns:
        str: a message telling the user what to do
    """
    if best_sf < 1:
        return ("No material passes. Try a taller beam, a shorter beam, "
                "or a smaller load.")
    return ("Best choice: " + best_name + " (safety factor "
            + str(round(best_sf, 2)) + ")")

assert_equal(recommendation("Steel", 41.666),
             "Best choice: Steel (safety factor 41.67)")
assert_equal(recommendation("Wood", 0.5),
             "No material passes. Try a taller beam, a shorter beam, "
             "or a smaller load.")


def material_names(materials: list[Material]) -> list[str]:
    """
    Makes a list of just the names of the materials.

    Args:
        materials (list[Material]): the materials

    Returns:
        list[str]: each material's name, in order
    """
    names = []
    for material in materials:
        names.append(material.name)
    return names

assert_equal(material_names([Material("Steel", 200, 250),
                             Material("Wood", 11, 40)]),
             ["Steel", "Wood"])


def has_material(materials: list[Material], name: str) -> bool:
    """
    Checks whether a material with this name is already in the list.
    Ignores capital letters and extra spaces, so "steel " matches "Steel".

    Args:
        materials (list[Material]): the materials to search
        name (str): the name to look for

    Returns:
        bool: True if the name is already in the list, False otherwise
    """
    for material in materials:
        if material.name.lower() == name.strip().lower():
            return True
    return False

assert_equal(has_material(TEST_MATERIALS, "steel "), True)
assert_equal(has_material(TEST_MATERIALS, "Wood"), False)

@route
def index(state: State) -> Page:
    """
    The home page which shows the title, a short intro, the status message,
    and buttons to the other pages.
 
    Args:
        state (State): the current state
 
    Returns:
        Page: the home page
    """
    return Page(state, [
        Header("Beam Bending Sim"),
        state.status,
        "See how steel, aluminum, and wood handle the same beam.",
        Button("Set Up Beam", "beam_setup"),
        Button("Materials", "materials"),
        Button("Learn", "learn"),
    ])

assert_equal(
    index(State(2, 1000, 50, 100, TEST_MATERIALS, "Welcome!", False)),
    Page(State(2, 1000, 50, 100, TEST_MATERIALS, "Welcome!", False), [
        Header("Beam Bending Sim"),
        "Welcome!",
        "See how steel, aluminum, and wood handle the same beam.",
        Button("Set Up Beam", "beam_setup"),
        Button("Materials", "materials"),
        Button("Learn", "learn"),
    ]))

 
@route
def beam_setup(state: State) -> Page:
    """
    The beam setup page where the user enters the beam's size and load.
 
    Args:
        state (State): the current state
 
    Returns:
        Page: the setup page with text boxes for the beam values
    """
    return Page(state, [
        Header("Set Up Your Beam"),
        state.status,
        "Length (m):",
        TextBox("length", str(state.length)),
        "Load (N):",
        TextBox("load", str(state.load)),
        "Width (mm):",
        TextBox("width", str(state.width)),
        "Height (mm):",
        TextBox("height", str(state.height)),
        CheckBox("only_passing", state.only_passing),
        "Only show passing materials",
        Button("Calculate", "calculate"),
        Button("Home", "index"),
    ])
 
assert_equal(
    beam_setup(State(2, 1000, 50, 100, TEST_MATERIALS, "", False)),
    Page(State(2, 1000, 50, 100, TEST_MATERIALS, "", False), [
        Header("Set Up Your Beam"),
        "",
        "Length (m):",
        TextBox("length", "2"),
        "Load (N):",
        TextBox("load", "1000"),
        "Width (mm):",
        TextBox("width", "50"),
        "Height (mm):",
        TextBox("height", "100"),
        CheckBox("only_passing", False),
        "Only show passing materials",
        Button("Calculate", "calculate"),
        Button("Home", "index"),
    ]))

 
@route
def calculate(state: State, length: str, load: str, width: str,
              height: str, only_passing: bool) -> Page:
    """
    Checks the user's inputs. If they are all positive numbers, saves them
    and shows the results. Otherwise, shows an error on the setup page.

    Args:
        state (State): the current state
        length (str): beam length typed by the user
        load (str): load typed by the user
        width (str): width typed by the user
        height (str): height typed by the user
        only_passing (bool): whether to hide failing materials

    Returns:
        Page: the results page, or the setup page if there was an error
    """
    if (is_positive_number(length) and is_positive_number(load)
            and is_positive_number(width) and is_positive_number(height)):
        state.length = float(length)
        state.load = float(load)
        state.width = float(width)
        state.height = float(height)
        state.only_passing = only_passing
        state.status = "Results calculated!"
        return results(state)
    state.status = "Error: every value must be a positive number."
    return beam_setup(state)


@route
def results(state: State) -> Page:
    """
    Shows a side-by-side table of how each material handles the beam,
    plus a recommendation.

    Args:
        state (State): the current state

    Returns:
        Page: the results page
    """
    inertia = moment_of_inertia(state.width, state.height)
    stress = max_stress(state.load, state.length, state.height, inertia)
    rows = []
    best_name = ""
    best_sf = 0.0
    for material in state.materials:
        deflection = max_deflection(state.load, state.length,
                                    material.youngs_modulus, inertia)
        sf = safety_factor(material.yield_strength, stress)
        if sf >= 1:
            verdict = "pass"
        else:
            verdict = "fail"
        if sf > best_sf:
            best_sf = sf
            best_name = material.name
        if not state.only_passing or verdict == "pass":
            rows.append([material.name, round(deflection, 2),
                         round(stress, 2), round(sf, 2), verdict])
    return Page(state, [
        Header("Results: Side by Side"),
        state.status,
        Table(rows, ["Material", "Max Deflection (mm)", "Max Stress (MPa)",
                     "Safety Factor", "Result"]),
        recommendation(best_name, best_sf),
        Button("Change Beam", "beam_setup"),
        Button("Home", "index"),
    ])

TEST_TWO_MATERIALS = [Material("Steel", 200, 250), Material("Wood", 11, 40)]
assert_equal(
    results(State(10, 2000, 50, 100, TEST_TWO_MATERIALS, "", True)),
    Page(State(10, 2000, 50, 100, TEST_TWO_MATERIALS, "", True), [
        Header("Results: Side by Side"),
        "",
        Table([["Steel", 50.0, 60.0, 4.17, "pass"]],
              ["Material", "Max Deflection (mm)", "Max Stress (MPa)",
               "Safety Factor", "Result"]),
        "Best choice: Steel (safety factor 4.17)",
        Button("Change Beam", "beam_setup"),
        Button("Home", "index"),
    ]))

assert_equal(
    calculate(State(1, 1, 1, 1, TEST_MATERIALS, "", False),
              "2", "1000", "50", "100", False),
    Page(State(2.0, 1000.0, 50.0, 100.0, TEST_MATERIALS,
               "Results calculated!", False), [
        Header("Results: Side by Side"),
        "Results calculated!",
        Table([["Steel", 0.2, 6.0, 41.67, "pass"]],
              ["Material", "Max Deflection (mm)", "Max Stress (MPa)",
               "Safety Factor", "Result"]),
        "Best choice: Steel (safety factor 41.67)",
        Button("Change Beam", "beam_setup"),
        Button("Home", "index"),
    ]))

@route
def materials(state: State) -> Page:
    """
    Shows every material in the list, a form to add a new one,
    and a dropdown to remove one.

    Args:
        state (State): the current state

    Returns:
        Page: the materials page
    """
    content = [Header("Materials List"), state.status]
    for material in state.materials:
        content.append(material.name + ": E = "
                       + str(material.youngs_modulus) + " GPa, yield = "
                       + str(material.yield_strength) + " MPa")
    if len(state.materials) > 0:
        options = material_names(state.materials)
    else:
        options = ["(none)"]
    return Page(state, content + [
        "Add a material:",
        "Name:",
        TextBox("new_name", ""),
        "E (GPa):",
        TextBox("new_modulus", ""),
        "Yield strength (MPa):",
        TextBox("new_yield", ""),
        Button("Add", "add_material"),
        "Remove a material:",
        SelectBox("material_name", options),
        Button("Remove", "remove_material"),
        Button("Home", "index"),
    ])

assert_equal(
    materials(State(2, 1000, 50, 100, TEST_MATERIALS, "", False)),
    Page(State(2, 1000, 50, 100, TEST_MATERIALS, "", False), [
        Header("Materials List"),
        "",
        "Steel: E = 200 GPa, yield = 250 MPa",
        "Add a material:",
        "Name:",
        TextBox("new_name", ""),
        "E (GPa):",
        TextBox("new_modulus", ""),
        "Yield strength (MPa):",
        TextBox("new_yield", ""),
        Button("Add", "add_material"),
        "Remove a material:",
        SelectBox("material_name", ["Steel"]),
        Button("Remove", "remove_material"),
        Button("Home", "index"),
    ]))

@route
def add_material(state: State, new_name: str, new_modulus: str,
                 new_yield: str, material_name: str) -> Page:
    """
    Adds a new material to the list if the inputs are valid and the name
    is not already used.

    Args:
        state (State): the current state
        new_name (str): name of the new material
        new_modulus (str): its stiffness E in GPa, as typed
        new_yield (str): its yield strength in MPa, as typed
        material_name (str): the remove dropdown's value. Not used here, but
            Drafter sends every input on the page, so the route must accept it.

    Returns:
        Page: the materials page
    """
    if (new_name.strip() == "" or not is_positive_number(new_modulus)
            or not is_positive_number(new_yield)):
        state.status = ("Error: enter a name and positive numbers "
                        "for E and yield strength.")
    elif has_material(state.materials, new_name):
        state.status = new_name.strip() + " is already in the list."
    else:
        state.materials.append(Material(new_name.strip(),
                                        float(new_modulus),
                                        float(new_yield)))
        state.status = "Added " + new_name.strip() + "!"
    return materials(state)

added_state = State(2, 1000, 50, 100, [Material("Steel", 200, 250)],
                    "", False)
add_material(added_state, "Titanium", "114", "880", "Steel")
assert_equal(added_state.materials,
             [Material("Steel", 200, 250), Material("Titanium", 114, 880)])
assert_equal(added_state.status, "Added Titanium!")

@route
def remove_material(state: State, new_name: str, new_modulus: str,
                    new_yield: str, material_name: str) -> Page:
    """
    Removes the chosen material from the list.

    Args:
        state (State): the current state
        new_name (str): from the add form. Not used here, but Drafter sends
            every input on the page, so the route must accept it.
        new_modulus (str): from the add form (not used here)
        new_yield (str): from the add form (not used here)
        material_name (str): the material chosen in the dropdown

    Returns:
        Page: the materials page
    """
    kept = []
    for material in state.materials:
        if material.name != material_name:
            kept.append(material)
    if len(kept) == len(state.materials):
        state.status = "There was nothing to remove."
    else:
        state.status = "Removed " + material_name + "."
    state.materials = kept
    return materials(state)

remove_state = State(2, 1000, 50, 100, [Material("Steel", 200, 250),
                                        Material("Wood", 11, 40)],
                     "", False)
remove_material(remove_state, "", "", "", "Wood")
assert_equal(remove_state.materials, [Material("Steel", 200, 250)])
assert_equal(remove_state.status, "Removed Wood.")


@route
def learn(state: State) -> Page:
    """
    Explains the beam bending concepts and formulas used by this site.

    Args:
        state (State): the current state

    Returns:
        Page: the learning page
    """
    return Page(state, [
        Header("Learn About Beam Bending"),

        Header("How Does a Beam Bend?", 2),
        ("A beam bends when a force is applied to it. The amount of "
         "bending depends on the beam's dimensions, the applied load, "
         "and the stiffness of its material."),
        ("This site uses a simply supported beam with a point load "
         "applied in the center."),

        Header("1. Moment of Inertia", 2),
        ("The area moment of inertia describes how resistant a "
         "beam's cross-section is to bending. For a rectangular beam:"),
        "I = (b * h^3) / 12",
        BulletedList([
            "I = moment of inertia (m^4)",
            "b = width of the beam (m)",
            "h = height of the beam (m)",
        ]),
        ("You enter width and height in mm. They are converted to "
         "meters before calculating."),
        ("A taller beam has a much greater moment of inertia because "
         "height is raised to the third power. This makes it more "
         "resistant to bending."),

        Header("2. Young's Modulus", 2),
        ("Young's modulus measures how stiff a material is. A higher "
         "value means the material is harder to stretch or compress "
         "and generally bends less under the same load."),
        BulletedList([
            "E = Young's modulus (Pa or GPa)",
        ]),

        Header("3. Maximum Deflection", 2),
        ("Deflection is how far a beam moves from its original "
         "position when a force is applied."),
        "δ_max = (P * L^3) / (48 * E * I)",
        BulletedList([
            "P = applied load (N)",
            "L = beam length (m)",
            "E = Young's modulus (Pa)",
            "I = moment of inertia (m^4)",
        ]),
        ("A smaller deflection means the beam bends less. Increasing "
         "stiffness or moment of inertia decreases deflection."),

        Header("4. Maximum Bending Stress", 2),
        ("Bending stress is the internal stress created when a beam "
         "bends. For this loading setup:"),
        "M_max = (P * L) / 4",
        "σ_max = (M_max * c) / I",
        BulletedList([
            "M_max = maximum bending moment (N*m)",
            "c = distance from the center to the outer edge (m)",
            "I = moment of inertia (m^4)",
            "σ_max = maximum bending stress (Pa)",
        ]),
        ("The maximum bending stress is the same for different "
         "materials when the beam dimensions and load are identical "
         "in this simplified model."),

        Header("5. Yield Strength and Factor of Safety", 2),
        ("Yield strength is the stress at which a material begins "
         "to permanently deform."),
        "Factor of Safety = Yield Strength / Maximum Stress",
        ("A factor of safety greater than or equal to 1 means the "
         "calculated stress does not exceed the material's yield "
         "strength. A value below 1 means it exceeds yield strength."),
        BulletedList([
            "pass: Factor of Safety >= 1",
            "fail: Factor of Safety < 1",
        ]),

        Header("6. Understanding Material Differences", 2),
        ("Young's modulus affects how much a beam bends. Yield "
         "strength affects whether the material passes the strength "
         "check. A material can bend less but still have a lower "
         "factor of safety."),

        Header("7. Limitations", 2),
        ("This site is an educational tool, not a professional "
         "structural engineering program. It assumes a simply "
         "supported beam, a centered point load, a rectangular "
         "cross-section, and uniform material properties. It does "
         "not account for buckling, fatigue, defects, or other "
         "real-world conditions."),

        Button("Back to Home", "index"),
        Button("Set Up a Beam", "beam_setup"),
    ])

learn_page = learn(State(2, 1000, 50, 100, TEST_MATERIALS, "", False))
assert_equal(learn_page.content[0], Header("Learn About Beam Bending"))

start_server(State(2.0, 1000.0, 50.0, 100.0, [
    Material("Steel", 200, 250),
    Material("Aluminum", 69, 276),
    Material("Wood", 11, 40),
], "", False))

