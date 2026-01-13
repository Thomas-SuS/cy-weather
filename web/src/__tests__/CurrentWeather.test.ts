import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CurrentWeather from '../components/CurrentWeather.vue'

describe('CurrentWeather', () => {
  it('affiche le chargement', () => {
    const wrapper = mount(CurrentWeather, {
      props: { weather: null, loading: true, error: null }
    })
    expect(wrapper.text()).toContain('Chargement')
  })

  it('affiche une erreur', () => {
    const wrapper = mount(CurrentWeather, {
      props: { weather: null, loading: false, error: 'Ville non trouvée' }
    })
    expect(wrapper.text()).toContain('Ville non trouvée')
  })

  it('affiche les données météo', () => {
    const weather = {
      city: 'Paris',
      country: 'FR',
      timestamp: '2026-01-13T12:00:00',
      weather: {
        temperature: 8.5,
        feels_like: 6.2,
        humidity: 75,
        pressure: 1015,
        wind_speed: 12.5,
        description: 'Couvert',
        icon: '04d'
      }
    }
    const wrapper = mount(CurrentWeather, {
      props: { weather, loading: false, error: null }
    })
    expect(wrapper.text()).toContain('Paris')
    expect(wrapper.text()).toContain('Couvert')
  })
})
