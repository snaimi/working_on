/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 18:09:04 by snaimi           ###   ########.fr       */
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
		pthread_cond_init(&data->dongles[i].cond, NULL);
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
		pthread_cond_destroy(&data->dongles[i].cond);
		heap_destroy(&data->dongles[i].queue);
		i++;
	}
	free(data->dongles);
}

void	release_dongles(t_coder *coder)
{
	long long	now;
	long long	cd;

	now = get_time_ms();
	cd = coder->data->metrics.dongle_cooldown;
	pthread_mutex_lock(&coder->left_dongle->mutex);
	coder->left_dongle->in_use = 0;
	coder->left_dongle->cooldown_until = now + cd;
	pthread_cond_broadcast(&coder->left_dongle->cond);
	pthread_mutex_unlock(&coder->left_dongle->mutex);
	pthread_mutex_lock(&coder->right_dongle->mutex);
	coder->right_dongle->in_use = 0;
	coder->right_dongle->cooldown_until = now + cd;
	pthread_cond_broadcast(&coder->right_dongle->cond);
	pthread_mutex_unlock(&coder->right_dongle->mutex);
}

int	take_dongles(t_coder *coder)
{
	t_dongle	*f;
	t_dongle	*s;

	f = coder->left_dongle;
	s = coder->right_dongle;
	if (coder->left_dongle->id >= coder->right_dongle->id)
	{
		f = coder->right_dongle;
		s = coder->left_dongle;
	}
	if (!acquire_one_dongle(coder, f))
		return (0);
	if (!acquire_one_dongle(coder, s))
		return (0);
	return (1);
}
