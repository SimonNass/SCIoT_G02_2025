; SCIoT_G02_2025 example problem

(define (problem example)

(:domain SCIoT_G02_2025)

(:objects
    green_led - light_switch_a
    blue_led - light_switch_a
    red_led - light_switch_a
)

(:init
    (is_activated green_led)
)

(:goal
    (and
        (is_activated green_led)
        (is_activated blue_led)
        (is_activated red_led)
    )
)
)