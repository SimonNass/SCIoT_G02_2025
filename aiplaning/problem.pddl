; SCIoT_G02_2025 example problem

(define (problem example)

(:domain SCIoT_G02_2025)

(:objects
    green_led - light_switch_a
    blue_led - light_switch_a
    red_led - light_switch_a
)

(:init
    (is_on green_led)
)

(:goal
    (and
        (is_on green_led)
        (is_on blue_led)
        (is_on red_led)
    )
)
)