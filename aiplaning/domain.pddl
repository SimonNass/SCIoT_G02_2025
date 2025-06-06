; SCIoT_G02_2025 domain

(define (domain SCIoT_G02_2025)

(:requirements :adl)
; :adl >>> :strips :typing :negative-preconditions :equality :disjunctive-preconditions

(:types floor room sensor actuator - object
   
    binary_s numerical_s textual_s - sensor
    button_s motion_s virtual_switch_s - binary_s
    temperature_s humidity_s light_s sound_s rotation_s virtual_dimmer_s - numerical_s
    ; - textual_s

    binary_a numerical_a textual_a - actuator
    switch_a light_switch_a virtual_switch_a - binary_a
    light_dimmer_a virtual_dimmer_a - numerical_a
    display_a - textual_a
)

(:predicates
    ; topology
    (room_is_part_of_floor ?room - room ?floor - floor) ; is the room part of this floor
    (sensor_is_part_of_room ?sensor - sensor ?room - room) ; is the sensor part of this room
    (actuator_is_part_of_room ?actuator - actuator ?room - room) ; is the actuator part of this room
    (actuator_increases_sensor ?actuator - actuator ?sensor - sensor) ; is the actuator influencing this sensor
    (actuator_decreases_sensor ?actuator - actuator ?sensor - sensor) ; is the actuator influencing this sensor
    (is_next_to ?room1 - room ?room2 - room) ; are the rooms next to each other

    ;; meta context
    (is_ocupied ?room - room) ; is the room ocupied
    (will_become_ocupied ?room - room) ; is the room ocupied in the near future
    (is_cleaned ?room - room) ; is the room cleaned

    ; activity
    (is_doing_sleep ?person_in_room - room) ; some people in this room are sleeping
    (is_doing_bath ?person_in_room - room) ; some people in this room are in the bathroom
    (is_doing_read ?person_in_room - room) ; some people in this room are reading

    ; sensors
    (is_sensing ?sensor - sensor) ; is the sensor prodicing a signal
    ;(is_verylow ?sensor - numerical_s) ; non binary sensor level
    (is_low ?sensor - numerical_s) ; non binary sensor level
    (is_ok ?sensor - numerical_s) ; non binary sensor level
    (is_high ?sensor - numerical_s) ; non binary sensor level
    ;(is_veryhigh ?sensor - numerical_s) ; non binary sensor level

    ; actuators
    (is_activated ?actuator - actuator) ; is a actuator activated

)


; cleaning
(:action simple_random_clean
    :parameters (?room1 - room)
    :precondition (and
        (not (is_cleaned ?room1))
        (not (is_ocupied ?room1))
        (not (will_become_ocupied ?room1))
        (forall (?room2 - room)
            (imply 
                (and
                    (not (= ?room1 ?room2))
                    (or
                        (is_next_to ?room1 ?room2)
                        (is_next_to ?room2 ?room1)
                    )
                )
                (or
                    (is_cleaned ?room2)
                    (is_ocupied ?room2)
                    (will_become_ocupied ?room2)
                )
            )
        )
    )
    :effect (and
        (is_cleaned ?room1)
    )
)

(:action sequence_clean
    :parameters (?room1 - room)
    :precondition (and
        (not (is_cleaned ?room1))
        (not (is_ocupied ?room1))
        (not (will_become_ocupied ?room1))
        (exists (?room2 - room)
            (and
                (not (= ?room1 ?room2))
                (or
                    (is_next_to ?room1 ?room2)
                    (is_next_to ?room2 ?room1)
                )
                (not (is_cleaned ?room2))
                (not (is_ocupied ?room2))
                (not (will_become_ocupied ?room2))
                (forall (?room3 - room)
                    (imply 
                        (and
                            (not (= ?room1 ?room3))
                            (not (= ?room2 ?room3))
                            (or
                                (is_next_to ?room1 ?room3)
                                (is_next_to ?room3 ?room1)
                            )
                        )
                        (or
                            (is_cleaned ?room3)
                            (is_ocupied ?room3)
                            (will_become_ocupied ?room3)
                        )
                    )
                )
            )
        )
    )
    :effect (and
        (is_cleaned ?room1)
    )
)

(:action cyclic_clean
    :parameters (?room1 - room)
    :precondition (and
        (not (is_cleaned ?room1))
        (not (is_ocupied ?room1))
        (not (will_become_ocupied ?room1))
        (or            
            (exists (?room2 ?room3 - room)
                (and
                    (not (= ?room1 ?room2))
                    (not (= ?room1 ?room3))
                    (not (= ?room2 ?room3))
                    (or
                        (is_next_to ?room1 ?room2)
                        (is_next_to ?room2 ?room1)
                    )
                    (or
                        (is_next_to ?room2 ?room3)
                        (is_next_to ?room3 ?room2)
                    )
                    (or
                        (is_next_to ?room1 ?room3)
                        (is_next_to ?room3 ?room1)
                    )
                    (not (is_cleaned ?room2))
                    (not (is_ocupied ?room2))
                    (not (will_become_ocupied ?room2))
                    (not (is_cleaned ?room3))
                    (not (is_ocupied ?room3))
                    (not (will_become_ocupied ?room3))
                )
            )
            (exists (?room2 ?room3 ?room4 - room)
                (and
                    (not (= ?room1 ?room2))
                    (not (= ?room1 ?room3))
                    (not (= ?room1 ?room4))
                    (not (= ?room2 ?room3))
                    (not (= ?room2 ?room4))
                    (not (= ?room3 ?room4))
                    (or
                        (is_next_to ?room1 ?room2)
                        (is_next_to ?room2 ?room1)
                    )
                    (or
                        (is_next_to ?room2 ?room3)
                        (is_next_to ?room3 ?room2)
                    )
                    (or
                        (is_next_to ?room3 ?room4)
                        (is_next_to ?room4 ?room3)
                    )
                    (or
                        (is_next_to ?room1 ?room4)
                        (is_next_to ?room4 ?room1)
                    )
                    (not (is_cleaned ?room2))
                    (not (is_ocupied ?room2))
                    (not (will_become_ocupied ?room2))
                    (not (is_cleaned ?room3))
                    (not (is_ocupied ?room3))
                    (not (will_become_ocupied ?room3))
                    (not (is_cleaned ?room4))
                    (not (is_ocupied ?room4))
                    (not (will_become_ocupied ?room4))
                )
            )
            (exists (?room2 ?room3 ?room4 ?room5 - room)
                (and
                    (not (= ?room1 ?room2))
                    (not (= ?room1 ?room3))
                    (not (= ?room1 ?room4))
                    (not (= ?room1 ?room5))
                    (not (= ?room2 ?room3))
                    (not (= ?room2 ?room4))
                    (not (= ?room2 ?room5))
                    (not (= ?room3 ?room4))
                    (not (= ?room3 ?room5))
                    (not (= ?room4 ?room5))
                    (or
                        (is_next_to ?room1 ?room2)
                        (is_next_to ?room2 ?room1)
                    )
                    (or
                        (is_next_to ?room2 ?room3)
                        (is_next_to ?room3 ?room2)
                    )
                    (or
                        (is_next_to ?room3 ?room4)
                        (is_next_to ?room4 ?room3)
                    )
                    (or
                        (is_next_to ?room4 ?room5)
                        (is_next_to ?room5 ?room4)
                    )
                    (not (is_cleaned ?room2))
                    (not (is_ocupied ?room2))
                    (not (will_become_ocupied ?room2))
                    (not (is_cleaned ?room3))
                    (not (is_ocupied ?room3))
                    (not (will_become_ocupied ?room3))
                    (not (is_cleaned ?room4))
                    (not (is_ocupied ?room4))
                    (not (will_become_ocupied ?room4))
                    (not (is_cleaned ?room5))
                    (not (is_ocupied ?room5))
                    (not (will_become_ocupied ?room5))
                )
            )
        )
    )
    :effect (and
        (is_cleaned ?room1)
    )
)

; actuator control
(:action turn_on
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (not (is_sensing ?sensor))
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_sensing ?sensor)
        (is_activated ?actuator)
    )
)

(:action turn_off
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_sensing ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_sensing ?sensor))
        (not (is_activated ?actuator))
    )
)

(:action turn_on_inverted
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (not (is_sensing ?sensor))
        (is_activated ?actuator)
    )
    :effect (and
        (is_sensing ?sensor)
        (not (is_activated ?actuator))
    )
)

(:action turn_off_inverted
    :parameters (?sensor - binary_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_sensing ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (not (is_sensing ?sensor))
        (is_activated ?actuator)
    )
)

(:action increase_s_by_a_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_low ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
        (not (is_low ?sensor))
        (is_ok ?sensor)
    )
)

(:action increase_s_by_na_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_low ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
        (not (is_low ?sensor))
        (is_ok ?sensor)
    )
)

; can only influence one sensor at a time
(:action decrerase_s_by_a_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_decreases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_high ?sensor)
        (not (is_activated ?actuator))
    )
    :effect (and
        (is_activated ?actuator)
        (not (is_high ?sensor))
        (is_ok ?sensor)
    )
)

(:action decrerase_s_by_na_in_r
    :parameters (?sensor - numerical_s ?actuator - actuator ?room - room)
    :precondition (and
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator ?room)
        (actuator_increases_sensor ?actuator ?sensor)
        (or 
            (is_ocupied ?room)
            (will_become_ocupied ?room)
        )
        (is_high ?sensor)
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))
        (not (is_high ?sensor))
        (is_ok ?sensor)
    )
)

; what if actuator of another room influences this sensor
(:action cancle_out_actuator
    :parameters (?sensor - numerical_s ?actuator_1 ?actuator_2 - actuator ?room - room)
    :precondition (and
        (not (= ?actuator_1 ?actuator_2))
        (sensor_is_part_of_room ?sensor ?room)
        (actuator_is_part_of_room ?actuator_1 ?room)
        (actuator_is_part_of_room ?actuator_2 ?room)
        (actuator_increases_sensor ?actuator_1 ?sensor)
        (actuator_decreases_sensor ?actuator_2 ?sensor)
        (is_activated ?actuator_1)
        (is_activated ?actuator_2)
    )
    :effect (and
        (not (is_activated ?actuator_1))
        (not (is_activated ?actuator_2))

    )
)

(:action save_energy
    :parameters (?actuator - actuator ?room - room)
    :precondition (and
        (actuator_is_part_of_room ?actuator ?room)
        (not (is_ocupied ?room))
        (not (will_become_ocupied ?room))
        (is_activated ?actuator)
    )
    :effect (and
        (not (is_activated ?actuator))

    )
)

)