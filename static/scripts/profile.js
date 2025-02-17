// Обработчик для повторной отправки письма подтверждения
document
	.getElementById('resendVerification')
	?.addEventListener('click', function (e) {
		e.preventDefault()

		fetch('/resend-verification/', {
			method: 'POST',
			headers: {
				'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
					.value,
			},
			credentials: 'same-origin',
		})
			.then(response => response.json())
			.then(data => {
				if (data.status === 'success') {
					alert('Письмо подтверждения отправлено')
				} else {
					alert('Ошибка при отправке письма: ' + data.message)
				}
			})
			.catch(error => {
				console.error('Error:', error)
				alert('Произошла ошибка при отправке запроса')
			})
	})
