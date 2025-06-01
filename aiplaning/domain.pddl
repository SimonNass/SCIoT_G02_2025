; SCIoT_G02_2025 domain

(define (domain SCIoT_G02_2025)

(:requirements :strips :typing :negative-preconditions)

(:types floor room sensor actuator - object
    temperature_s humidity_s light_s sound_s rotation_s button_s motion_s - sensor
    light_a switch_a display_a - actuator
    light_dimmer_a light_switch_a - light_a
)

(:predicates
    (is_part_of ?room - room ?floor - floor) ; is the room part of this floor
    ;(is_part_of ?sensor - sensor ?room - room) ; is the sensor part of this room
    ;(is_part_of ?actuator - actuator ?room - room) ; is the actuator part of this room
    (is_next_to ?room1 - room ?room2 - room) ; are the rooms next to each other
    (is_ocupied ?room - room) ; is the room ocupied
    (is_cleaned ?room - room) ; is the room cleaned
    (is_pressed ?button - button_s) ; is the button pressed
    (detects_motion ?motion - motion_s) ; is a motion detected
    (is_on ?light - light_a) ; is a lightsource on
)

; this action turns on the light
(:action turn_on
    :parameters (?light - light_switch_a)
    :precondition (and
        ; we only ever need to do it once
        (not (is_on ?light))
    )
    :effect (and
        (is_on ?light)
    )
)
(:action turn_off
    :parameters (?light - light_switch_a)
    :precondition (and
        ; we only ever need to do it once
        (is_on ?light)
    )
    :effect (and
        (not (is_on ?light))
    )
)
(:action increase_light
    :parameters (?light - light_a)
    :precondition (and
        ; we only ever need to do it once
        (not (is_on ?light))
    )
    :effect (and
        (is_on ?light)
    )
)
(:action decrease_light
    :parameters (?light - light_a)
    :precondition (and
        ; we only ever need to do it once
        (is_on ?light)
    )
    :effect (and
        (not (is_on ?light))
    )
)

)