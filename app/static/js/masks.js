// Brazilian format masks for form fields
document.addEventListener('DOMContentLoaded', function() {
    // Phone mask (55 54 99999-9999)
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 13) value = value.slice(0, 13);
            
            let formatted = '';
            if (value.length > 0) {
                formatted = value.slice(0, 2); // country code
                if (value.length > 2) {
                    formatted += ' ' + value.slice(2, 4); // area code
                    if (value.length > 4) {
                        if (value.length > 9) {
                            formatted += ' ' + value.slice(4, 9) + '-' + value.slice(9);
                        } else {
                            formatted += ' ' + value.slice(4);
                        }
                    }
                }
            }
            e.target.value = formatted;
        });
    }
    
    // CPF mask (000.000.000-00)
    const cpfInput = document.getElementById('id_cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            
            let formatted = '';
            if (value.length > 0) {
                formatted = value.slice(0, 3);
                if (value.length > 3) {
                    formatted += '.' + value.slice(3, 6);
                    if (value.length > 6) {
                        formatted += '.' + value.slice(6, 9);
                        if (value.length > 9) {
                            formatted += '-' + value.slice(9);
                        }
                    }
                }
            }
            e.target.value = formatted;
        });
    }
    
    // CNPJ mask (00.000.000/0000-00)
    const cnpjInput = document.getElementById('id_cnpj');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 14) value = value.slice(0, 14);
            
            let formatted = '';
            if (value.length > 0) {
                formatted = value.slice(0, 2);
                if (value.length > 2) {
                    formatted += '.' + value.slice(2, 5);
                    if (value.length > 5) {
                        formatted += '.' + value.slice(5, 8);
                        if (value.length > 8) {
                            formatted += '/' + value.slice(8, 12);
                            if (value.length > 12) {
                                formatted += '-' + value.slice(12);
                            }
                        }
                    }
                }
            }
            e.target.value = formatted;
        });
    }
    
    // CEP mask (00000-000)
    const cepInput = document.getElementById('id_postal_code');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            
            let formatted = '';
            if (value.length > 0) {
                formatted = value.slice(0, 5);
                if (value.length > 5) {
                    formatted += '-' + value.slice(5);
                }
            }
            e.target.value = formatted;
        });
    }
    
    // State field - convert to uppercase and limit to 2 chars
    const stateInput = document.getElementById('id_state');
    if (stateInput) {
        stateInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase().slice(0, 2);
        });
    }
});


