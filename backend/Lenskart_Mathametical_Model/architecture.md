Architecture Overview: The Automated Store Layout Generator
1. The Elevator Pitch: What is this Application?
This application is an automated interior designer for our retail stores.

Imagine you have an empty room (a 2D floor plan image) and a list of all the furniture and displays you need to put inside. Instead of a person manually dragging and dropping each item in a design program, this tool does it automatically. It takes the floor plan and the furniture list, and in a matter of seconds, it generates a perfect, professional 2D store layout in a CAD (.dxf) format, following all our brand and placement rules.

2. Who Are Our Users?
The primary users of this tool are our internal design and store planning teams. The goal is to dramatically speed up the process of creating initial store layouts, which is a critical step when opening a new retail location. The final output helps everyone, including project managers and the sales team, visualize the new store accurately.


3. The Main Parts (Explained Like an Automated Designer)
Think of this system as a brilliant robot designer with a team of specialists. Here are the main parts:

The Input (The Client's Request)
The robot designer needs two things to start:


The Floor Plan: A simple image (.png) of the empty store's layout.


The Furniture List: A configuration list in the main.py file that tells the designer how many of each fixture (like display cases, tables, and chairs) to use. This is often based on the store's size and sales goals.



The main.py file (The Project Manager)
This is the control panel where our teams give the main instructions. It kicks off the entire process by telling the robot designer which floor plan to use and what furniture to place inside.


The Backend (The Robot Designer and its Specialist Team)
This is the engine room where all the magic happens. It consists of three key specialists:

CV_Controller.py (The Surveyor):
This specialist acts like a high-tech surveyor. It receives the floor plan image and uses Computer Vision to analyze it. It automatically finds the walls, measures the exact dimensions of the room, and even calculates the correct scale (e.g., millimeters per pixel) by reading any measurements written on the plan. The output is a precise digital blueprint.

Fixture.py (The Warehouse Manager):
This specialist manages our entire furniture catalog. For every single item—from a small chair to a large display wall—it reads the item's individual design file (.dxf). It calculates the exact dimensions (width and height) and, most importantly, identifies the perfect "handle" (the bottom-left corner) for placing it. This ensures every piece of furniture is placed with perfect alignment.


DXF_Controller.py (The Master Planner):
This is the robot designer itself—the brains of the operation. It takes the digital blueprint from the Surveyor and the furniture list from the Project Manager. Then, following a sophisticated set of rules, it strategically places every fixture. It knows exactly where things should go, for example:

Placing 

clinic rooms in the corners.



Arranging 

central display units (Euro_centre) in the middle of the floor.



Sequentially lining up 

wall display units along the left and right walls.



Intelligently avoiding collisions between all objects.

The assets/ folder (The Furniture Catalog)
This folder is our digital warehouse. It contains a .dxf design file for every single piece of furniture, fixture, and display that can be placed in a store. The Warehouse Manager (Fixture.py) uses this catalog to get the specs for each item before the Master Planner (DXF_Controller.py) places it.

4. A User's Journey: How It Works in Practice
Here is a step-by-step story of how our team uses the tool:

Get the Brief: A designer receives a floor plan image for a new store location.


Define the Order: They open main.py and define the "merch mix"—the exact number of jj_fixture_medium, Euro_centre, and Clinic_regular fixtures needed for that store.

Press Go: The designer runs the script.


Surveying (CV_Controller): The system first analyzes the image to create a perfect digital outline of the room.

Smart Placement (DXF_Controller): The Master Planner gets the room outline and starts placing fixtures one by one, following its logic. It grabs each fixture's dimensions from the Furniture Catalog via the Warehouse Manager.


The Result: Within seconds, a complete and professional CAD file named floorplan_new.dxf is generated, showing the fully furnished store layout, ready for the next stage of the design process.


5. Key Selling Points & Business Value
This automation provides immense value to our business:

🚀 Extreme Speed: It transforms the store layout process from a manual task that could take hours or days into an automated one that completes in seconds.


✔️ Consistency: Every layout is generated using a standard set of rules, ensuring brand guidelines are always met. This eliminates the small variations that come from different designers working manually.


🧠 Data-Driven Layouts: The fixture list can be directly influenced by sales data. We can create layouts that are optimized for revenue by prioritizing the placement of high-performing product displays.

🎯 High Accuracy: The system automatically handles all the complex geometric calculations, placing every item precisely and ensuring there are no overlaps or mistakes, which reduces costly errors down the line.

---
## 6. Additional Resources

* **Design Workflow & Fixture Details:** For a deeper look into the manual design process this application automates and for details on fixture placement strategies, please see the [Design Workflow Document](https://drive.google.com/file/d/1gfkEY-EAmj8RCv255GL-NBjc_ZKQlle5/view?usp=sharing).

* **Fixture & Merchandising Data:** A complete list of all fixtures, their types, and the merchandising mix logic can be found in our [Project Google Sheet](https://docs.google.com/spreadsheets/d/1jbgU6pdC3uPaMX30AtmU4vDzvn4T3R6ZAvykzfoPBro/edit?usp=sharing).
Fixture & Merchandising Data: A complete list of all fixtures, their types, and the merchandising mix logic can be found in our Project Google Sheet.