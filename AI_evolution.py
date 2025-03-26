import time
from ollama import chat
from ollama import ChatResponse

class Simulation:
    def __init__(self, grid_size_x=10, grid_size_y=10):
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        # Initialize two points
        self.point1 = [grid_size_x // 3, grid_size_y // 3]  # Point 1 starts in the top-left third
        self.point2 = [2 * grid_size_x // 3, grid_size_y // 3]  # Point 2 starts in the bottom-right third
        self.grid = [[0 for _ in range(grid_size_y)] for _ in range(grid_size_x)]
        self.point1_alive = True
        self.point2_alive = True
        self.update_grid()

    def update_grid(self):
        # Clear the grid and update the positions of the two points
        self.grid = [[0 for _ in range(self.grid_size_y)] for _ in range(self.grid_size_x)]
        if self.point1_alive:
            self.grid[self.point1[1]][self.point1[0]] = 1  # Mark point 1
        if self.point2_alive:
            self.grid[self.point2[1]][self.point2[0]] = 2  # Mark point 2

    def get_direction_from_model(self, point_number, model_name):
        # Convert the grid to a string representation
        grid_text = '\n'.join(' '.join(str(cell) for cell in row) for row in self.grid)
        
        prompt = f'''Here is the current grid:\n{grid_text}\n  
                    You are point {point_number} on the grid (marked as {point_number}).
                    Respond with only the word "up", "down", "left", "right", or "shoot".
                    Lower case only. 
                    Moving "up" decreases the y-coordinate.
                    Moving "down" increases the y-coordinate.
                    Moving "left" decreases the x-coordinate.
                    Moving "right" increases the x-coordinate.
                    If the other point is next to you (horizontally or vertically adjacent), you can shoot to eliminate them by saying "shoot".
                    I want you to eliminate the other players. They are the other non-0 numbers.'''
        #print(f"Prompt to AI for Point {point_number}:\n{prompt}\n")  # Debug: Print the prompt
        response: ChatResponse = chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        direction = response['message']['content']
        print(f"AI Response for Point {point_number}: {direction}")  # Debug: Print the AI's response
        return direction

    def move_point(self, point, point_number, model_name):
        # Get direction from the Ollama model
        direction = self.get_direction_from_model(point_number, model_name)
        print(f"Moving Point {point_number} {direction}")
        
        # Check if the other point is adjacent
        other_point = self.point2 if point_number == 1 else self.point1
        other_alive = self.point2_alive if point_number == 1 else self.point1_alive
        if direction == "shoot" and other_alive and abs(point[0] - other_point[0]) + abs(point[1] - other_point[1]) == 1:
            print(f"Point {point_number} shot the other point!")
            if point_number == 1:
                self.point2_alive = False
            else:
                self.point1_alive = False
            return  # End the move if a shot is fired

        # Move the point if no shot is fired
        if direction == 'up' and point[1] > 0:
            point[1] -= 1
        elif direction == 'down' and point[1] < self.grid_size_y - 1:
            point[1] += 1
        elif direction == 'left' and point[0] > 0:
            point[0] -= 1
        elif direction == 'right' and point[0] < self.grid_size_x - 1:
            point[0] += 1

    def print_grid(self):
        self.update_grid()  # Update the grid with the latest positions
        for row in self.grid:
            print(' '.join(str(cell) for cell in row))
        print("\n" + "-"*20 + "\n")

    def run(self, steps=100):
        for _ in range(steps):
            if self.point1_alive:
                self.move_point(self.point1, 1, 'llama3')  # Use model 'llama3' for point 1
            if self.point2_alive:
                self.move_point(self.point2, 2, 'deepseek-v2:16b')  # Use model 'llama2' for point 2
            self.print_grid()
            if not self.point1_alive or not self.point2_alive:
                print("Game over!")
                break
            #time.sleep(0.1)  # Pause for a short time to visualize the movement

if __name__ == "__main__":
    sim = Simulation()
    sim.run(steps=1000)