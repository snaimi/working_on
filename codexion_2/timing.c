/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   timing.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:54:27 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

long long	get_time_ms(void)
{
	struct timeval	tv;

	gettimeofday(&tv, NULL);
	return ((tv.tv_sec * 1000LL) + (tv.tv_usec / 1000));
}

void	precise_sleep(long long duration_ms, t_data *data)
{
	long long	start;

	start = get_time_ms();
	while (get_time_ms() - start < duration_ms)
	{
		pthread_mutex_lock(&data->state_mutex);
		if (data->simulation_over)
		{
			pthread_mutex_unlock(&data->state_mutex);
			break ;
		}
		pthread_mutex_unlock(&data->state_mutex);
		usleep(500);
	}
}