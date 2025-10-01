/*
 * Copyright (c) 2025 Sunnie Kapar
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_ttihp_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire load_en = ui_in[0];
  wire count_en = ui_in[1];
  wire output_en = ui_in[2];
  wire [7:0] load_data = uio_in;

  wire [7:0] counter_value;

  counter counter_inst (
    .clk(clk),
    .rst_n(rst_n),
    .load(load_en),
    .load_data(load_data),
    .count_en(count_en),
    .count(counter_value)
  );

  assign uo_out = output_en ? counter_value : 8'bz;

  // Unused outputs
  assign uio_out = 8'b0;
  assign uio_oe = 8'b0;
  
  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[7:3], 1'b0};

endmodule

module counter (
  input wire clk,
  input wire rst_n,
  input wire load,
  input wire [7:0] load_data,
  input wire count_en,
  output wire [7:0] count
);

  reg [7:0] count_reg;

  assign count = count_reg;

  always @(posedge clk or negedge rst_n) begin
    if (rst_n == 0) begin
      count_reg <= 8'b0;
    end else begin
      if (load) begin
        count_reg <= load_data;
      end else if (count_en) begin
        count_reg <= count_reg + 1'b1;
      end
    end 
  end

endmodule