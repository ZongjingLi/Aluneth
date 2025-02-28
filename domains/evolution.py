import arcade
import pymunk
import timeit
import math

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Shadows of Angrathar"


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 2
        self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height


def make_body(env, name, x, y, friction = 43.9, mass = 30.0, box_shape = None):
    
    if box_shape is None:
        box_shape = (32,32)
    moment = pymunk.moment_for_box(mass, box_shape)
    body = pymunk.Body(mass, moment)
    body.position = pymunk.Vec2d(x, y)
    shape = pymunk.Poly.create_box(body, box_shape)
    shape.elasticity = 0.001
    shape.friction = 43.9
    env.space.add(body, shape)

    sprite = BoxSprite(shape, "/Users/melkor/Documents/datasets/PatchWork/{}".format(name), width=box_shape[0], height=box_shape[1])
    env.sprite_list.append(sprite)

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color((61,77,86))
        self.paused = False
        self.hold = 0

        # grabber 
        self.graber_x = 200.0
        self.graber_y = 200.0
        self.graber_angl = 0.0

        # -- Pymunk
        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (0.0, -900.0)

        # Lists of sprites or lines
        self.sprite_list: arcade.SpriteList[PhysicsSprite] = arcade.SpriteList()
        self.static_lines = []

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        # Create the floor
        floor_height = 80
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, [0, floor_height], [SCREEN_WIDTH, floor_height], 0.0)
        shape.friction = 20
        self.space.add(shape, body)
        self.static_lines.append(shape)



        size = 32

        # Create the stacks of boxes

        for row in range(5):
            for column in range(4):
                pass
                #make_body(self, "crafting_table_gondolin_bottom.png",
                # 300 + column* size,
                #  size * row + (floor_height + size / 2), friction = 500, mass =100)

        for row in range(5):
            for column in range(4):
                pass
                #make_body(self, "pillar1_pettyDwarf_side.png",
                # 500 + column* size,
                #  size * row + (floor_height + size / 2), friction = 100, mass =15000)

        for row in range(5):
            for column in range(4):
                make_body(self, "crafting_table_brethil_bottom.png",
                 700 + column* size,
                  size * row + (floor_height + size / 2), friction = 500, mass =1000)

        #make_body(self, "tol_in_gaurhoth_torch.png", 900, (floor_height + size / 2), mass = 100)
        #make_body(self, "tolingaurhoth_gate_base.png", 900, (floor_height + size / 2 * 5), mass = 5000, box_shape=(32 * 4,32*1))
        #make_body(self, "tolingaurhoth_gate_base.png", 900, (floor_height + size / 2 * 7), mass = 5000, box_shape=(32 * 4,32*1))
        

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Draw all the sprites
        self.sprite_list.draw()

        # Draw the lines that aren't sprites
        for line in self.static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, (39,45,52), 2)


        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

        arcade.draw_text("+", self.graber_x,self.graber_y, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time
        

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.last_mouse_position = x, y
            # See if we clicked on anything
            shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())

            # If we did, remember what we clicked on
            if len(shape_list) > 0:
                self.shape_being_dragged = shape_list[0]

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            # With right mouse button, shoot a heavy coin fast.
            mass = 999
            radius = 20
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            body.position = x, y
            body.velocity = 1000, 10
            shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            shape.friction = 9999999.1
            self.space.add(body, shape)

            sprite = CircleSprite(shape, "assets/images/ice.png")
            self.sprite_list.append(sprite)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Release the item we are holding (if any)
            self.shape_being_dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # If we are holding an object, move it with the mouse
            self.last_mouse_position = x, y
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = dx * 20, dy * 20

    def save_states(self):
        for sprite in self.sprite_list:
            x = sprite.pymunk_shape.position.x
            y = sprite.pymunk_shape.position.y

    def on_key_press(self, symbol, modifiers):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause/Unpause the game
        I/J/K/L: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.Q:
            # Quit immediately
            arcade.close_window()
        step = 15
        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.I or symbol == arcade.key.UP:
            self.graber_y += step

        if symbol == arcade.key.K or symbol == arcade.key.DOWN:
            self.graber_y -= step

        if symbol == arcade.key.J or symbol == arcade.key.LEFT:
            self.graber_x -= step

        if symbol == arcade.key.L or symbol == arcade.key.RIGHT:
            self.graber_x += step

    def on_update(self, delta_time):
        start_time = timeit.default_timer()

        # Check for balls that fall off the screen
        for sprite in self.sprite_list:
            if sprite.pymunk_shape.body.position.y < 0:
                # Remove balls from physics space
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                # Remove balls from physics list
                sprite.remove_from_sprite_lists()

        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # https://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(1 / 60.0)

        # If we are dragging an object, make sure it stays with the mouse. Otherwise
        # gravity will drag it down.
        if self.shape_being_dragged is not None:
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = 0, 0

        # Move sprites to where physics objects are
        for sprite in self.sprite_list:
            sprite.center_x = sprite.pymunk_shape.body.position.x
            sprite.center_y = sprite.pymunk_shape.body.position.y
            sprite.angle = math.degrees(sprite.pymunk_shape.body.angle)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    arcade.run()


if __name__ == "__main__":
    main()