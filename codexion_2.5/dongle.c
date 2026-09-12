/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/12 00:24:56 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	init_dongles(t_data *data)
{
	int	i;

	data->dongles = malloc(sizeof(t_dongle) * data->metrics.number_of_coders);
	if (!data->dongles)
		return ;
	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		data->dongles[i].id = i;
		data->dongles[i].in_use = 0;
		data->dongles[i].cooldown_until = 0;
		pthread_mutex_init(&data->dongles[i].mutex, NULL);
		heap_init(&data->dongles[i].queue, data->metrics.number_of_coders);
		i++;
	}
}

void	destroy_dongles(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->metrics.number_of_coders)
	{
		pthread_mutex_destroy(&data->dongles[i].mutex);
		heap_destroy(&data->dongles[i].queue);
		i++;
	}
	free(data->dongles);
}

void	release_dongles(t_coder *coder)
{
	long long	now;
	long long	cd;
	t_dongle	*f;
	t_dongle	*s;

	f = coder->left_dongle;
	s = coder->right_dongle;
	now = get_time_ms();
	cd = coder->data->metrics.dongle_cooldown;
	pthread_mutex_lock(&f->mutex);
	f->in_use = 0;
	f->cooldown_until = now + cd;
	pthread_mutex_unlock(&f->mutex);
	if (s != f)
	{
		pthread_mutex_lock(&s->mutex);
		s->in_use = 0;
		s->cooldown_until = now + cd;
		pthread_mutex_unlock(&s->mutex);
	}
}
