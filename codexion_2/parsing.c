/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:53:49 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static long long	ft_atoll(const char *str)
{
	long long	res;
	int			i;

	res = 0;
	i = 0;
	while (str[i] == ' ' || (str[i] >= 9 && str[i] <= 13))
		i++;
	if (str[i] == '+')
		i++;
	while (str[i] >= '0' && str[i] <= '9')
	{
		res = (res * 10) + (str[i] - '0');
		i++;
	}
	if (str[i] != '\0')
		return (-1);
	return (res);
}

static int	ft_strcmp(const char *s1, const char *s2)
{
	int	i;

	i = 0;
	while (s1[i] && s2[i] && s1[i] == s2[i])
		i++;
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}

static int	parse_scheduler(int argc, char **argv, t_metrics *m)
{
	int	idx;

	if (argc == 9)
	{
		m->dongle_cooldown = ft_atoll(argv[7]);
		idx = 8;
	}
	else
	{
		m->dongle_cooldown = 0;
		idx = 7;
	}
	if (ft_strcmp(argv[idx], "edf") == 0)
		m->scheduler = SCHEDULER_EDF;
	else if (ft_strcmp(argv[idx], "fifo") == 0)
		m->scheduler = SCHEDULER_FIFO;
	else
		return (0);
	return (1);
}

int	parse_arguments(int argc, char **argv, t_metrics *metrics)
{
	if (argc < 8 || argc > 9)
		return (0);
	metrics->number_of_coders = ft_atoll(argv[1]);
	metrics->time_to_burnout = ft_atoll(argv[2]);
	metrics->time_to_compile = ft_atoll(argv[3]);
	metrics->time_to_debug = ft_atoll(argv[4]);
	metrics->time_to_refactor = ft_atoll(argv[5]);
	metrics->number_of_compiles_required = ft_atoll(argv[6]);
	if (!parse_scheduler(argc, argv, metrics))
		return (0);
	if (metrics->number_of_coders <= 0 || metrics->time_to_burnout <= 0
		|| metrics->time_to_compile < 0 || metrics->time_to_debug < 0
		|| metrics->time_to_refactor < 0 || metrics->dongle_cooldown < 0)
		return (0);
	if (metrics->number_of_compiles_required <= 0)
		metrics->number_of_compiles_required = -1;
	return (1);
}