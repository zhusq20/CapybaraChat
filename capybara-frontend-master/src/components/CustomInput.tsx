import React, { useEffect } from "react";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";

export default function CustomInput(props: any) {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      props.onEnter();
    }
  };

  return (
    <Box>
      <label style={{ fontWeight: "bold" }} htmlFor={props.id}>
        {props.title}
      </label>
      <TextField
        label={props.label}
        fullWidth
        margin="dense"
        size="medium"
        id={props.id}
        name={props.name}
        value={props.value}
        onChange={props.onChange}
        disabled={props.dis}
        required={props.req}
        type={props.type}
        InputProps={props.InputProps}
        select={props.select}
        onKeyDown={handleKeyDown}
      >
        {props.content}
      </TextField>
    </Box>
  );
}
