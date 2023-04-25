$("#calc-form").submit(function(event) {
    event.preventDefault();
    const formData = $(this).serialize();
    $.post("/calculate", formData, function(response) {
      if (response.error) {
        $("#result").html(`<p>${response.error}</p>`);
      } else {
        $("#result").html(`
          <p>The tilting point where the 3P(Seller) business model becomes more profitable is at a price of ${response.tilting_point}</p>
          <p>Profit for both models at the tilting point is: ${response.profit_3P_Seller}</p>
          <p>The hypotheses include a Seller fee of 15%, VAT rate of 20%, a TACOS of 10% and an Amazon margin of 30%.</p>
        `);
      }
    });
  });
  