import pygame
from pygame import Vector2

from ball import Ball


class Goals:
    post_radius = 5.

    def __init__(self, screen, left_pos: Vector2, right_pos: Vector2):
        self.screen = screen
        self.left_pos = left_pos
        self.right_pos = right_pos

    def draw(self):
        pygame.draw.circle(
            self.screen,
            color="white",
            center=self.left_pos,
            radius=self.post_radius
        )
        pygame.draw.circle(
            self.screen,
            color="white",
            center=self.right_pos,
            radius=self.post_radius
        )
        # post_diff = self.right_pos - self.left_pos
        # pygame.draw.line(self.screen, "black", self.left_pos, self.left_pos + post_diff)

    def check_goal(self, ball: Ball, dt: float):
        # Check if path taken by ball intersects goal line
        # Using cross product solution provided by
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        # @gareth-rees
        
        if ball.shape.vel.magnitude() == 0.:
            return

        post_diff = self.right_pos - self.left_pos
        # ball_pos_old = ball.shape.pos - ball.shape.vel * dt
        # ball_trail = - ball.shape.pos + ball_pos_old
        ball_trail = - ball.shape.vel * 5 * dt
        ball_pos_ghost = ball.shape.pos + ball_trail

        try:
            t = (ball.shape.pos - self.left_pos).cross(ball_trail)\
                / (post_diff.cross(ball_trail))

            u = (ball.shape.pos - self.left_pos).cross(post_diff)\
                / (post_diff.cross(ball_trail))
            
            pygame.draw.line(self.screen, "black", ball.shape.pos, ball_pos_ghost)
            return 0 <= t <= 1 and 0 <= u <= 1

        except ZeroDivisionError:
            return False