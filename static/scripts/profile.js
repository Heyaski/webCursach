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

// Добавляем валидацию для поля "Расскажите о себе"
document.getElementById('aboutMe')?.addEventListener('input', function () {
	const submitButton = document.querySelector('button[name="save_info"]')
	const errorDiv = document.getElementById('aboutMeError') || createErrorDiv()

	// Получаем текст и удаляем лишние пробелы в начале и конце
	let value = this.value.trim()

	// Проверяем на пустой текст или текст из одних пробелов
	if (!value || /^\s+$/.test(value)) {
		showError('Пожалуйста, введите текст')
		submitButton.disabled = true
		return
	}

	// Фильтруем запрещенные слова
	const forbiddenWords = ['арбуз', 'козявка', 'жопа', 'дурак']

	let hasFilteredWords = false
	let filteredText = value

	forbiddenWords.forEach(word => {
		const regex = new RegExp(word, 'gi')
		if (regex.test(filteredText)) {
			hasFilteredWords = true
			filteredText = filteredText.replace(regex, '*'.repeat(word.length))
		}
	})

	// Если были найдены запрещенные слова, обновляем текст
	if (hasFilteredWords) {
		this.value = filteredText
		showError('Обнаружены и заменены запрещенные слова')
		submitButton.disabled = true
		return
	}

	// Проверяем минимальное количество слов (не считая пробелы)
	const words = filteredText.split(/\s+/).filter(word => word.length > 0)
	if (words.length < 2) {
		showError('Введите минимум два слова')
		submitButton.disabled = true
		return
	}

	// Проверяем наличие букв
	if (!/[A-Za-zА-Яа-я]/.test(filteredText)) {
		showError('Текст должен содержать буквы')
		submitButton.disabled = true
		return
	}

	// Если все проверки пройдены
	errorDiv.remove()
	submitButton.disabled = false

	function createErrorDiv() {
		const div = document.createElement('div')
		div.id = 'aboutMeError'
		div.className = 'alert alert-danger mt-2'
		return div
	}

	function showError(message) {
		errorDiv.textContent = message
		if (!errorDiv.parentElement) {
			document.getElementById('aboutMe').parentElement.appendChild(errorDiv)
		}
	}
})

// Добавляем валидацию для поля города
document.getElementById('cityInput')?.addEventListener('input', function () {
	const submitButton = document.querySelector('button[name="save_info"]')
	const errorDiv = document.getElementById('cityError') || createCityErrorDiv()

	// Получаем значение поля и удаляем пробелы в начале и конце
	let value = this.value.trim()

	// Проверяем наличие английских букв
	if (/[a-zA-Z]/.test(value)) {
		showCityError('Используйте только русские буквы')
		this.value = value.replace(/[a-zA-Z]/g, '')
		submitButton.disabled = true
		return
	}

	// Проверяем наличие специальных символов и цифр
	if (/[^а-яА-ЯёЁ\s-]/.test(value)) {
		showCityError('Используйте только русские буквы и дефис')
		this.value = value.replace(/[^а-яА-ЯёЁ\s-]/g, '')
		submitButton.disabled = true
		return
	}

	// Проверяем, что поле не пустое и не состоит только из пробелов
	if (!value || /^\s*$/.test(value)) {
		showCityError('Введите название города')
		submitButton.disabled = true
		return
	}

	// Если все проверки пройдены
	if (errorDiv) {
		errorDiv.remove()
	}
	submitButton.disabled = false

	function createCityErrorDiv() {
		const div = document.createElement('div')
		div.id = 'cityError'
		div.className = 'alert alert-danger mt-2'
		return div
	}

	function showCityError(message) {
		errorDiv.textContent = message
		if (!errorDiv.parentElement) {
			document.getElementById('cityInput').parentElement.appendChild(errorDiv)
		}
	}
})
