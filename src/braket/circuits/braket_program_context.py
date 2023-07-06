from typing import List, Tuple

import numpy as np

from braket.circuits import Circuit, Instruction
from braket.circuits.gates import Unitary
from braket.circuits.translations import (
    BRAKET_GATES,
    braket_noise_gate_to_instruction,
    braket_result_to_result_type,
)
from braket.default_simulator import KrausOperation
from braket.default_simulator.openqasm.program_context import AbstractProgramContext
from braket.ir.jaqcd.program_v1 import Results


class BraketProgramContext(AbstractProgramContext):
    def __init__(self):
        super().__init__()
        self.circuit = Circuit()

    def is_builtin_gate(self, name: str) -> bool:
        """Whether the gate is currently in scope as a built-in Braket gate.

        Args:
            name (str): name of the built-in Braket gate

        Returns:
            bool: return TRUE if it is a built-in gate else FALSE.
        """
        user_defined_gate = self.is_user_defined_gate(name)
        return name in BRAKET_GATES and not user_defined_gate

    def add_phase_instruction(self, target: Tuple[int], phase_value: int) -> None:
        raise NotImplementedError

    def add_gate_instruction(
        self, gate_name: str, target: Tuple[int], *params, ctrl_modifiers: List[int], power: float
    ) -> None:
        """Add Braket gate to the circuit.

        Args:
            gate_name (str): name of the built-in Braket gate.
            target (Tuple[int]): control_qubits + target_qubits.
            ctrl_modifiers (List[int]): Quantum state on which to control the
                operation. Must be a binary sequence of same length as number of qubits in
                `control-qubits` in target. For example "0101", [0, 1, 0, 1], 5 all represent
                controlling on qubits 0 and 2 being in the \\|0⟩ state and qubits 1 and 3 being
                in the \\|1⟩ state.
            power(float): Integer or fractional power to raise the gate to.
        """
        target_qubits = target[len(ctrl_modifiers) :]
        control_qubits = target[: len(ctrl_modifiers)]
        instruction = Instruction(
            BRAKET_GATES[gate_name](*params[0]),
            target=target_qubits,
            control=control_qubits,
            control_state=ctrl_modifiers,
            power=power,
        )
        self.circuit.add_instruction(instruction)

    def add_custom_unitary(
        self,
        unitary: np.ndarray,
        target: Tuple[int],
    ) -> None:
        """Add a custom Unitary instruction to the circuit

        Args:
            unitary (np.ndarray): unitary matrix
            target (Tuple[int]): control_qubits + target_qubits
        """
        instruction = Instruction(Unitary(unitary)(), target)
        self.circuit.add_instruction(instruction)

    def add_noise_instruction(self, noise: KrausOperation) -> None:
        """Add a noise instruction the circuit"""
        self.circuit.add_instruction(braket_noise_gate_to_instruction(noise))

    def add_result(self, result: Results) -> None:
        """Add a result type to the circuit"""
        self.circuit.add_result_type(braket_result_to_result_type(result))
